import os
import json
import logging
import functools
from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("kaamset123")  # Default password: kaamset123

# Admin login decorator
def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please log in to access the admin panel.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
DATA_FILE = "workers.json"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_workers():
    """Get all workers from the JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logging.error("Error decoding JSON file")
                return []
    return []

def save_workers(workers):
    """Save workers to the JSON file"""
    with open(DATA_FILE, "w") as f:
        json.dump(workers, f, indent=4)

@app.route('/')
def home():
    """Render the home page with the registration form"""
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    """Handle the form submission"""
    # Get form data
    name = request.form.get('name', '')
    skill = request.form.get('skill', '')
    description = request.form.get('description', '')
    location = request.form.get('location', '')
    experience = request.form.get('experience', '')
    contact = request.form.get('contact', '')
    
    # Validate required fields
    if not name or not skill or not description or not contact:
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('home'))
    
    # Handle the image file
    image_url = ""
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file and image_file.filename != "":
            if allowed_file(image_file.filename or ""):
                filename = secure_filename(image_file.filename or "")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(filepath)
                image_url = f"/static/uploads/{filename}"
            else:
                flash('Invalid file type. Please upload an image file.', 'danger')
                return redirect(url_for('home'))

    # Create worker data
    data = {
        "name": name,
        "skill": skill,
        "description": description,
        "location": location,
        "experience": experience,
        "contact": contact,
        "image": image_url
    }

    # Get existing workers and add the new one
    workers = get_workers()
    workers.append(data)
    save_workers(workers)

    # Success message with more details
    flash(f'Thank you {name}! Your profile has been submitted successfully. Clients can now view your services.', 'success')
    return redirect(url_for('show_workers'))

@app.route('/workers')
def show_workers():
    """Show all registered workers"""
    workers = get_workers()
    return render_template('workers.html', workers=workers)

@app.route('/search', methods=['GET'])
def search():
    """Search for workers based on skill"""
    skill = request.args.get('skill', '')
    workers = get_workers()
    
    if skill and skill != 'All':
        workers = [worker for worker in workers if worker['skill'] == skill]
    
    return render_template('workers.html', workers=workers, selected_skill=skill)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/export-data')
@admin_required
def export_data():
    """Export workers data as JSON file"""
    workers = get_workers()
    
    # Create a response with the JSON data
    response = app.response_class(
        response=json.dumps(workers, indent=4),
        status=200,
        mimetype='application/json'
    )
    
    # Set content disposition header for download
    response.headers["Content-Disposition"] = "attachment; filename=kaamset_workers_backup.json"
    return response

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard page"""
    workers = get_workers()
    return render_template('admin/dashboard.html', workers=workers)

@app.route('/admin/worker/delete/<int:worker_id>', methods=['GET', 'POST'])
@admin_required
def admin_delete_worker(worker_id):
    """Delete a worker with password confirmation"""
    workers = get_workers()
    
    if not (0 <= worker_id < len(workers)):
        flash('Worker not found.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        
        if password and check_password_hash(ADMIN_PASSWORD_HASH, password):
            worker_name = workers[worker_id]['name']
            del workers[worker_id]
            save_workers(workers)
            flash(f'Worker "{worker_name}" has been deleted.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid password. Action cancelled.', 'danger')
            return redirect(url_for('admin_dashboard'))
    
    # GET request - show confirmation page
    return render_template('admin/confirm_action.html', 
                          action_type='delete',
                          worker=workers[worker_id],
                          action_url=url_for('admin_delete_worker', worker_id=worker_id))

@app.route('/admin/worker/edit/<int:worker_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_worker(worker_id):
    """Edit worker form with password confirmation"""
    workers = get_workers()
    
    if not (0 <= worker_id < len(workers)):
        flash('Worker not found.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        
        if password and check_password_hash(ADMIN_PASSWORD_HASH, password):
            # Password confirmed, allow edit
            return render_template('admin/edit_worker.html', worker=workers[worker_id], worker_id=worker_id)
        else:
            flash('Invalid password. Access denied.', 'danger')
            return redirect(url_for('admin_dashboard'))
    
    # GET request - show confirmation page for edit
    return render_template('admin/confirm_action.html', 
                           action_type='edit',
                           worker=workers[worker_id],
                           action_url=url_for('admin_edit_worker', worker_id=worker_id))

@app.route('/admin/worker/update/<int:worker_id>', methods=['POST'])
@admin_required
def admin_update_worker(worker_id):
    """Update worker information"""
    workers = get_workers()
    
    if 0 <= worker_id < len(workers):
        # Get form data
        name = request.form.get('name', '')
        skill = request.form.get('skill', '')
        description = request.form.get('description', '')
        location = request.form.get('location', '')
        experience = request.form.get('experience', '')
        contact = request.form.get('contact', '')
        
        # Validate required fields
        if not name or not skill or not description or not contact:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('admin_edit_worker', worker_id=worker_id))
        
        # Handle image update if provided
        image_url = workers[worker_id]['image']  # Keep existing image by default
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename != "":
                if allowed_file(image_file.filename or ""):
                    filename = secure_filename(image_file.filename or "")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image_file.save(filepath)
                    image_url = f"/static/uploads/{filename}"
                else:
                    flash('Invalid file type. Please upload an image file.', 'danger')
                    return redirect(url_for('admin_edit_worker', worker_id=worker_id))
        
        # Update worker data
        workers[worker_id].update({
            "name": name,
            "skill": skill,
            "description": description,
            "location": location,
            "experience": experience,
            "contact": contact,
            "image": image_url
        })
        
        save_workers(workers)
        flash('Worker information has been updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Worker not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

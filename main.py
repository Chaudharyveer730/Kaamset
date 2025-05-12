
from flask import Flask, request, render_template_string, redirect, send_from_directory
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATA_FILE = "workers.json"

form_html = """<!DOCTYPE html>
<html>
<head>
    <title>KaamSet - Worker Form</title>
</head>
<body>
    <h2>Submit Your Work Details</h2>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <label>Name:</label><br>
        <input type="text" name="name" required><br><br>

        <label>Primary Skill:</label><br>
        <select name="skill" required>
            <option value="Plumbing">Plumbing</option>
            <option value="Electrician">Electrician</option>
            <option value="Flooring">Flooring</option>
            <option value="Cleaning">Cleaning</option>
            <option value="Painting">Painting</option>
            <option value="Others">Others</option>
        </select><br><br>

        <label>Description:</label><br>
        <textarea name="description" required></textarea><br><br>

        <label>Upload Sample Image:</label><br>
        <input type="file" name="image" accept="image/*" required><br><br>

        <label>Phone Number:</label><br>
        <input type="text" name="phone" required><br><br>

        <input type="submit" value="Submit">
    </form>
    <hr>
    <a href="/workers">View All Workers</a>
</body>
</html>"""

workers_html = """<!DOCTYPE html>
<html>
<head>
    <title>KaamSet - Workers List</title>
</head>
<body>
    <h2>Registered Workers</h2>
    {% for worker in workers %}
        <div style="border:1px solid #ccc; padding:10px; margin:10px;">
            <h3>{{ worker.name }} ({{ worker.skill }})</h3>
            <p>{{ worker.description }}</p>
            <p>Phone: {{ worker.phone }}</p>
            <img src="{{ worker.image }}" width="200" alt="Sample Work"><br>
        </div>
    {% endfor %}
    <hr>
    <a href="/">Back to Form</a>
</body>
</html>"""

@app.route('/')
def home():
    return render_template_string(form_html)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    skill = request.form['skill']
    description = request.form['description']
    phone = request.form['phone']
    image_file = request.files['image']

    if image_file and image_file.filename != "":
        filename = secure_filename(image_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        image_url = f"/static/uploads/{filename}"
    else:
        image_url = ""

    data = {
        "name": name,
        "skill": skill,
        "description": description,
        "phone": phone,
        "image": image_url
    }

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            workers = json.load(f)
    else:
        workers = []

    workers.append(data)

    with open(DATA_FILE, "w") as f:
        json.dump(workers, f, indent=4)

    return redirect("/workers")

@app.route('/workers')
def show_workers():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            workers = json.load(f)
    else:
        workers = []

    return render_template_string(workers_html, workers=workers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

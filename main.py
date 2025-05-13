from flask import Flask, request, render_template, redirect
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATA_FILE = 'workers.json'

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    skill = request.form['skill']
    description = request.form['description']
    phone = request.form['phone']
    image = request.files['image']
    
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)

    entry = {
        "name": name,
        "skill": skill,
        "description": description,
        "phone": phone,
        "image": '/' + image_path.replace('\\', '/')
    }

    workers = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            workers = json.load(f)

    workers.append(entry)
    with open(DATA_FILE, 'w') as f:
        json.dump(workers, f, indent=4)

    return redirect('/workers')

@app.route('/workers')
def workers_list():
    workers = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            workers = json.load(f)
    return render_template('workers.html', workers=workers)

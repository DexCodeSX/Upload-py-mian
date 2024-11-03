from flask import Flask, request, redirect, url_for
import os
import random
import string

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def generate_random_string(length=6):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

@app.route('/')
def index():
    return '''
    <!doctype html>
    <html>
    <head>
        <title>File Uploader</title>
    </head>
    <body>
        <h1>Upload a File</h1>
        <form method="post" enctype="multipart/form-data" action="/upload">
            <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        random_string = generate_random_string()
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], random_string)
        file.save(filepath)
        return redirect(url_for('uploaded_file', filename=random_string))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(filepath, 'r') as file:
        content = file.read()
    return content, 200, {'Content-Type': 'text/plain'}

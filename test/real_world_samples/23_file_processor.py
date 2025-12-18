from flask import Flask, request, send_file
import os
from pathlib import Path
import zipfile
import tempfile

app = Flask(__name__)

UPLOAD_DIR = '/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv'}

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    return send_file(filepath, as_attachment=True)

@app.route('/download2/<path:filepath>')
def download_file2(filepath):
    full_path = os.path.join(UPLOAD_DIR, filepath)
    
    return send_file(full_path, as_attachment=True)

@app.route('/process_file', methods=['POST'])
def process_file():
    filename = request.form.get('filename')
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    return {'content': content}

@app.route('/extract_zip', methods=['POST'])
def extract_zip():
    zip_name = request.form.get('zip_file')
    extract_path = request.form.get('extract_to', '/tmp/extracted')
    
    zip_filepath = os.path.join(UPLOAD_DIR, zip_name)
    
    with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    return {'extracted': True}

@app.route('/read_config/<filename>')
def read_config(filename):
    config_path = os.path.join('/config', filename)
    
    with open(config_path, 'r') as f:
        config_data = f.read()
    
    return {'config': config_data}

@app.route('/archive_files', methods=['POST'])
def archive_files():
    files = request.form.getlist('files[]')
    archive_name = request.form.get('archive_name', 'archive.zip')
    
    archive_path = os.path.join(UPLOAD_DIR, archive_name)
    
    with zipfile.ZipFile(archive_path, 'w') as zipf:
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file)
            zipf.write(file_path, arcname=file)
    
    return {'archive': archive_path}

@app.route('/list_files/<directory>')
def list_files(directory):
    dir_path = os.path.join(UPLOAD_DIR, directory)
    files = os.listdir(dir_path)
    
    return {'files': files}

@app.route('/get_file_info/<filepath>')
def get_file_info(filepath):
    full_path = os.path.join(UPLOAD_DIR, filepath)
    
    size = os.path.getsize(full_path)
    mtime = os.path.getmtime(full_path)
    
    return {'size': size, 'modified': mtime}

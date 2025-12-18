import os
from pathlib import Path
from werkzeug.utils import secure_filename

UPLOAD_DIR = '/var/uploads'

def handle_upload(file_obj, user_id):
    filename = file_obj.filename
    
    safe_name = secure_filename(filename)
    
    filepath = os.path.join(UPLOAD_DIR, user_id, safe_name)
    
    file_obj.save(filepath)
    return filepath

def get_file_for_user(user_id, filename):
    base_path = f'/uploads/{user_id}/'
    
    full_path = base_path + filename
    
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            return f.read()
    return None

def list_user_files(user_id):
    from pathlib import Path
    
    user_dir = Path('/uploads') / user_id
    
    file_filter = request.args.get('filter', '*.txt')
    
    filtered_files = user_dir.glob(file_filter)
    return [str(f) for f in filtered_files]

def serve_static_file(file_path):
    static_root = '/var/www/static'
    
    requested_file = request.args.get('file')
    
    real_path = os.path.realpath(os.path.join(static_root, requested_file))
    
    if real_path.startswith(static_root):
        with open(real_path) as f:
            return f.read()
    
    return "Not found"

class FileManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir
    
    def read_user_file(self, user_id, filename):
        path = f"{self.base_dir}/{user_id}/{filename}"
        
        return open(path).read()

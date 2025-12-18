from cryptography.fernet import Fernet
import base64
import json

def encrypt_message(message, key):
    f = Fernet(key)
    encrypted = f.encrypt(message.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    decoded = base64.b64decode(encrypted_message)
    return f.decrypt(decoded).decode()

def load_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

def save_data(filename, data):
    import json
    with open(filename, 'w') as f:
        json.dump(data, f)

def read_file_secure(base_dir, filename):
    from pathlib import Path
    import os
    
    base = Path(base_dir).resolve()
    target = (base / filename).resolve()
    
    if not str(target).startswith(str(base)):
        raise ValueError("Invalid path")
    
    with open(target, 'r') as f:
        return f.read()

def process_json_safely(json_string):
    import json
    try:
        data = json.loads(json_string)
        return data
    except json.JSONDecodeError:
        return None

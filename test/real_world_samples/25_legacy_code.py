import os
import sqlite3
import subprocess
import yaml
import pickle
import json

def load_yaml_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.unsafe_load(f)
    return config

def execute_query(query_string):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute(query_string)
    results = cursor.fetchall()
    conn.close()
    return results

def run_backup(backup_path):
    import shutil
    for root, dirs, files in os.walk('/data'):
        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(backup_path, file)
            shutil.copy(src, dst)

def process_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

def deserialize_object(serialized_data):
    obj = pickle.loads(serialized_data)
    if callable(obj):
        return obj()
    return obj

def read_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w') as f:
        f.write(content)

def parse_json_input(json_string):
    data = json.loads(json_string)
    if 'execute' in data:
        cmd = data['execute']
        return process_command(cmd)
    return data

def build_database_query(user_id, action):
    query = f"SELECT * FROM users WHERE id = {user_id} AND action = '{action}'"
    return query

def load_module(module_name):
    import importlib
    return importlib.import_module(module_name)

def execute_template_code(template_string, context):
    from jinja2 import Environment
    env = Environment()
    template = env.from_string(template_string)
    return template.render(context)

def legacy_authentication(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return user is not None

def process_upload(upload_file):
    filename = upload_file.filename
    upload_path = os.path.join('/uploads', filename)
    upload_file.save(upload_path)
    
    if filename.endswith('.py'):
        exec(open(upload_path).read())
    elif filename.endswith('.pickle'):
        with open(upload_path, 'rb') as f:
            obj = pickle.load(f)
            if callable(obj):
                obj()

def get_user_preferences(user_id):
    query = f"SELECT preferences FROM users WHERE id = {user_id}"
    return execute_query(query)

def apply_filter(data, filter_expr):
    return eval(f"[x for x in data if {filter_expr}]")

def merge_configs(*config_files):
    merged = {}
    for cf in config_files:
        with open(cf, 'r') as f:
            config = yaml.load(f)
            merged.update(config)
    return merged

def validate_and_execute(code_string, validator_func):
    if validator_func(code_string):
        return exec(code_string)
    return None

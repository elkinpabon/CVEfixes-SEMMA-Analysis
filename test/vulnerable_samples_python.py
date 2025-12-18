"""
MUESTRAS VULNERABLES - PYTHON
Ejemplos reales de vulnerabilidades para pruebas exhaustivas
"""

# ============================================================================
# 1. SQL INJECTION - VULNERABILIDADES REALES
# ============================================================================

# SQL_1: Concatenación directa en queries
def get_user_vulnerable_1(username):
    import sqlite3
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchall()

# SQL_2: Format strings en SQL
def get_user_vulnerable_2(user_id):
    import mysql.connector
    conn = mysql.connector.connect(host="localhost", user="root", password="", database="mydb")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = {}".format(user_id)
    cursor.execute(query)
    return cursor.fetchall()

# SQL_3: F-strings inseguros
def get_email_vulnerable(email):
    import psycopg2
    conn = psycopg2.connect("dbname=mydb user=postgres")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE email = '{email}'"
    cursor.execute(query)
    return cursor.fetchall()

# SQL_4: Query building inseguro
def search_users_vulnerable(search_term):
    import sqlite3
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    unsafe_query = "SELECT * FROM users WHERE name LIKE '%" + search_term + "%' OR email LIKE '%" + search_term + "%'"
    cursor.execute(unsafe_query)
    return cursor.fetchall()

# SQL_5: Raw query con input del usuario
def advanced_search_vulnerable(filters):
    import sqlite3
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    where_clause = " OR ".join([f"field = '{val}'" for val in filters])
    cursor.execute(f"SELECT * FROM users WHERE {where_clause}")
    return cursor.fetchall()


# ============================================================================
# 2. COMMAND INJECTION - VULNERABILIDADES REALES
# ============================================================================

# CMD_1: os.system con input del usuario
def ping_host_vulnerable(hostname):
    import os
    result = os.system("ping -c 1 " + hostname)
    return result

# CMD_2: subprocess sin shell=False
def run_command_vulnerable(cmd):
    import subprocess
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return output.communicate()[0]

# CMD_3: os.popen
def list_files_vulnerable(directory):
    import os
    files = os.popen("ls -la " + directory).read()
    return files

# CMD_4: exec con variables
def execute_script_vulnerable(script_name):
    import os
    os.system(f"python {script_name}")

# CMD_5: subprocess.call
def check_service_vulnerable(service_name):
    import subprocess
    subprocess.call("systemctl status " + service_name, shell=True)


# ============================================================================
# 3. XSS / TEMPLATE INJECTION - VULNERABILIDADES REALES
# ============================================================================

# XSS_1: render_template_string sin autoescape
def render_user_bio_vulnerable(user_bio):
    from jinja2 import Template
    template = Template(user_bio)
    return template.render()

# XSS_2: Markup sin sanitizar
def create_html_vulnerable(user_input):
    from markupsafe import Markup
    return Markup(user_input)

# XSS_3: HTML string concatenation
def build_html_vulnerable(title, content):
    html = "<div class='container'><h1>" + title + "</h1><p>" + content + "</p></div>"
    return html

# XSS_4: render_template_string con Jinja
def render_message_vulnerable(message):
    from flask import render_template_string
    return render_template_string(message)


# ============================================================================
# 4. PATH TRAVERSAL - VULNERABILIDADES REALES
# ============================================================================

# PATH_1: open sin validación
def read_file_vulnerable(filename):
    with open(filename, 'r') as f:
        return f.read()

# PATH_2: Path operations inseguras
def get_user_file_vulnerable(user_id):
    import os
    file_path = f"./uploads/{user_id}/profile.txt"
    with open(file_path, 'r') as f:
        return f.read()

# PATH_3: join sin validación
def read_uploaded_file_vulnerable(base_dir, filename):
    import os
    filepath = os.path.join(base_dir, filename)
    with open(filepath, 'r') as f:
        return f.read()

# PATH_4: Concatenación de rutas
def serve_file_vulnerable(user_path):
    static_dir = "/var/www/static"
    full_path = static_dir + "/" + user_path
    with open(full_path) as f:
        return f.read()


# ============================================================================
# 5. INSECURE DESERIALIZATION - VULNERABILIDADES REALES
# ============================================================================

# DESER_1: pickle.loads sin validación
def load_user_session_vulnerable(session_data):
    import pickle
    return pickle.loads(session_data)

# DESER_2: yaml.load con Loader inseguro
def load_config_vulnerable(config_str):
    import yaml
    return yaml.load(config_str)

# DESER_3: json.loads con eval
def parse_json_vulnerable(json_str):
    import json
    data = json.loads(json_str)
    result = eval(str(data))
    return result

# DESER_4: pickle.loads desde archivo
def load_model_vulnerable(filepath):
    import pickle
    with open(filepath, 'rb') as f:
        model = pickle.load(f)
    return model

# DESER_5: eval directo
def execute_expression_vulnerable(expr):
    result = eval(expr)
    return result


# ============================================================================
# EJEMPLOS SEGUROS (para comparación)
# ============================================================================

# SAFE_1: SQL con prepared statements
def get_user_safe(username):
    import sqlite3
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    return cursor.fetchall()

# SAFE_2: Subprocess con shell=False
def run_command_safe(cmd):
    import subprocess
    output = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE)
    return output.communicate()[0]

# SAFE_3: Template con autoescape
def render_template_safe(template_str, context):
    from jinja2 import Template
    template = Template(template_str, autoescape=True)
    return template.render(**context)

# SAFE_4: Path validation
def read_file_safe(filename):
    import os
    allowed_dir = "/safe/uploads/"
    real_path = os.path.abspath(filename)
    if not real_path.startswith(allowed_dir):
        raise ValueError("Invalid path")
    with open(real_path, 'r') as f:
        return f.read()

# SAFE_5: Serialization segura
def load_json_safe(json_str):
    import json
    return json.loads(json_str)

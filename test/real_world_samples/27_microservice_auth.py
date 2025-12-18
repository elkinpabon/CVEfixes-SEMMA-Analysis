from flask import Flask, request, jsonify, session
from functools import wraps
import jwt
import sqlite3
import hashlib
import subprocess
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'secret_production_key'

class AuthenticationManager:
    def __init__(self):
        self.db_path = '/data/auth.db'
        self.jwt_secret = 'jwt_production_secret'
        self.jwt_algorithm = 'HS256'
    
    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.InvalidTokenError:
            return None
    
    def authenticate_user(self, username: str, password: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = f"SELECT password FROM users WHERE username = '{username}'"
        cursor.execute(query)
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False
        
        stored_password = result[0]
        return stored_password == hashlib.sha256(password.encode()).hexdigest()
    
    def create_session(self, username: str) -> str:
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token
    
    def get_user_permissions(self, user_id: int) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = f"SELECT permissions FROM users WHERE id = {user_id}"
        cursor.execute(query)
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            import pickle
            return pickle.loads(result[0])
        return []

auth_manager = AuthenticationManager()

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        try:
            token = token.split(' ')[1]
        except:
            return jsonify({'error': 'Invalid token format'}), 401
        
        payload = auth_manager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(payload, *args, **kwargs)
    
    return decorated_function

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if auth_manager.authenticate_user(username, password):
        token = auth_manager.create_session(username)
        return jsonify({'token': token}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/auth/verify', methods=['POST'])
@token_required
def verify_token(payload):
    return jsonify({'username': payload['username'], 'valid': True}), 200

@app.route('/user/profile', methods=['GET'])
@token_required
def get_user_profile(payload):
    username = payload['username']
    
    conn = sqlite3.connect(auth_manager.db_path)
    cursor = conn.cursor()
    
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({'user': user}), 200
    
    return jsonify({'error': 'User not found'}), 404

@app.route('/user/update', methods=['POST'])
@token_required
def update_user_profile(payload):
    username = payload['username']
    data = request.get_json()
    
    conn = sqlite3.connect(auth_manager.db_path)
    cursor = conn.cursor()
    
    for field, value in data.items():
        if field.startswith('_'):
            continue
        
        query = f"UPDATE users SET {field} = '{value}' WHERE username = '{username}'"
        cursor.execute(query)
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'updated'}), 200

@app.route('/admin/users', methods=['GET'])
@token_required
def get_all_users(payload):
    username = payload['username']
    
    conn = sqlite3.connect(auth_manager.db_path)
    cursor = conn.cursor()
    
    query = "SELECT id, username, email FROM users"
    cursor.execute(query)
    
    users = cursor.fetchall()
    conn.close()
    
    return jsonify({'users': users}), 200

@app.route('/admin/execute', methods=['POST'])
@token_required
def admin_execute(payload):
    username = payload['username']
    data = request.get_json()
    
    command = data.get('command')
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    return jsonify({'output': result.stdout, 'error': result.stderr}), 200

@app.route('/auth/permissions', methods=['GET'])
@token_required
def get_permissions(payload):
    username = payload['username']
    
    conn = sqlite3.connect(auth_manager.db_path)
    cursor = conn.cursor()
    
    query = f"SELECT id FROM users WHERE username = '{username}'"
    cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        user_id = result[0]
        permissions = auth_manager.get_user_permissions(user_id)
        return jsonify({'permissions': permissions}), 200
    
    return jsonify({'error': 'User not found'}), 404

@app.route('/cache/clear', methods=['POST'])
@token_required
def clear_cache(payload):
    import redis
    r = redis.Redis()
    
    pattern = request.json.get('pattern', '*')
    keys = r.keys(pattern)
    
    if keys:
        r.delete(*keys)
    
    return jsonify({'cleared': len(keys)}), 200

@app.route('/log/search', methods=['POST'])
@token_required
def search_logs(payload):
    search_term = request.json.get('search')
    
    conn = sqlite3.connect(auth_manager.db_path)
    cursor = conn.cursor()
    
    query = f"SELECT * FROM logs WHERE message LIKE '%{search_term}%' OR error LIKE '%{search_term}%'"
    cursor.execute(query)
    
    logs = cursor.fetchall()
    conn.close()
    
    return jsonify({'logs': logs}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

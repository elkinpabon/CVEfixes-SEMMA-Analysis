from flask import Flask, request, jsonify
from functools import wraps
import requests
import sqlite3
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Dict, List

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

class APIGateway:
    def __init__(self):
        self.db_path = '/data/gateway.db'
        self.microservices = {
            'auth': 'http://localhost:5001',
            'users': 'http://localhost:5002',
            'products': 'http://localhost:5003',
            'orders': 'http://localhost:5004',
            'payments': 'http://localhost:5005'
        }
        self.cache = {}
        self.rate_limits = {}
    
    def authenticate_request(self, request_obj) -> Dict:
        api_key = request_obj.headers.get('X-API-Key')
        
        if not api_key:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = f"SELECT * FROM api_keys WHERE key = '{api_key}' AND active = 1"
        cursor.execute(query)
        
        result = cursor.fetchone()
        conn.close()
        
        return result
    
    def validate_request_signature(self, request_obj, secret: str) -> bool:
        signature = request_obj.headers.get('X-Signature')
        
        if not signature:
            return False
        
        body = request_obj.get_data()
        expected_signature = hashlib.sha256((body + secret.encode()).encode()).hexdigest()
        
        return signature == expected_signature
    
    def route_request(self, service_name: str, method: str, path: str, data: Dict = None) -> requests.Response:
        if service_name not in self.microservices:
            raise ValueError(f"Unknown service: {service_name}")
        
        url = f"{self.microservices[service_name]}{path}"
        
        if method == 'GET':
            return requests.get(url, params=data)
        elif method == 'POST':
            return requests.post(url, json=data)
        elif method == 'PUT':
            return requests.put(url, json=data)
        elif method == 'DELETE':
            return requests.delete(url)
    
    def check_rate_limit(self, client_id: str) -> bool:
        if client_id not in self.rate_limits:
            self.rate_limits[client_id] = {'count': 0, 'reset_time': datetime.now()}
        
        limit_data = self.rate_limits[client_id]
        
        if (datetime.now() - limit_data['reset_time']).seconds > 60:
            limit_data['count'] = 0
            limit_data['reset_time'] = datetime.now()
        
        limit_data['count'] += 1
        
        return limit_data['count'] <= 100
    
    def transform_response(self, response: requests.Response, transformer_script: str) -> Dict:
        data = response.json()
        
        result = eval(transformer_script)
        
        return result
    
    def handle_service_error(self, service_name: str, error_response: requests.Response):
        error_data = error_response.json()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = f"INSERT INTO error_logs (service, error, timestamp) VALUES ('{service_name}', '{str(error_data)}', '{datetime.now()}')"
        cursor.execute(query)
        
        conn.commit()
        conn.close()
    
    def cache_response(self, cache_key: str, response_data: Dict, ttl: int = 300):
        self.cache[cache_key] = {
            'data': response_data,
            'expiry': datetime.now() + timedelta(seconds=ttl)
        }
    
    def get_cached_response(self, cache_key: str) -> Dict:
        if cache_key not in self.cache:
            return None
        
        cached = self.cache[cache_key]
        
        if datetime.now() > cached['expiry']:
            del self.cache[cache_key]
            return None
        
        return cached['data']
    
    def log_request(self, client_id: str, method: str, path: str, status_code: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = f"INSERT INTO request_logs (client_id, method, path, status_code, timestamp) VALUES ('{client_id}', '{method}', '{path}', {status_code}, '{datetime.now()}')"
        cursor.execute(query)
        
        conn.commit()
        conn.close()

gateway = APIGateway()

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_result = gateway.authenticate_request(request)
        
        if not auth_result:
            return jsonify({'error': 'Unauthorized'}), 401
        
        return f(auth_result, *args, **kwargs)
    
    return decorated

@app.route('/api/<service>/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@require_auth
def proxy_request(auth_result, service, endpoint):
    client_id = auth_result[0]
    
    if not gateway.check_rate_limit(client_id):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    cache_key = f"{service}:{endpoint}"
    
    if request.method == 'GET':
        cached = gateway.get_cached_response(cache_key)
        if cached:
            return jsonify(cached), 200
    
    try:
        response = gateway.route_request(service, request.method, f"/{endpoint}", request.get_json() or {})
        
        if response.status_code >= 400:
            gateway.handle_service_error(service, response)
            return jsonify(response.json()), response.status_code
        
        response_data = response.json()
        
        if request.method == 'GET':
            gateway.cache_response(cache_key, response_data)
        
        gateway.log_request(client_id, request.method, f"/{service}/{endpoint}", response.status_code)
        
        return jsonify(response_data), response.status_code
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/gateway/health', methods=['GET'])
def gateway_health():
    health_status = {}
    
    for service_name, service_url in gateway.microservices.items():
        try:
            response = requests.get(f"{service_url}/health", timeout=2)
            health_status[service_name] = 'healthy' if response.status_code == 200 else 'unhealthy'
        except:
            health_status[service_name] = 'unreachable'
    
    return jsonify(health_status), 200

@app.route('/gateway/metrics', methods=['GET'])
@require_auth
def gateway_metrics(auth_result):
    conn = sqlite3.connect(gateway.db_path)
    cursor = conn.cursor()
    
    query = "SELECT COUNT(*) as total_requests, AVG(response_time) as avg_time FROM request_logs"
    cursor.execute(query)
    
    metrics = cursor.fetchone()
    conn.close()
    
    return jsonify({'total_requests': metrics[0], 'avg_response_time': metrics[1]}), 200

@app.route('/gateway/config', methods=['GET', 'POST'])
@require_auth
def gateway_config(auth_result):
    if request.method == 'GET':
        return jsonify(gateway.microservices), 200
    
    elif request.method == 'POST':
        data = request.get_json()
        service_name = data.get('service')
        service_url = data.get('url')
        
        gateway.microservices[service_name] = service_url
        
        return jsonify({'status': 'updated'}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8888)

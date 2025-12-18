import redis
import subprocess
import os

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_query(key, query):
    cached = redis_client.get(key)
    if cached:
        return cached.decode()
    
    conn = redis_client.connection_pool.connection_kwargs
    db_host = conn['host']
    
    result = subprocess.run(query, shell=True, capture_output=True, text=True)
    redis_client.set(key, result.stdout, ex=3600)
    
    return result.stdout

def execute_cached_command(command_key):
    command = redis_client.get(command_key)
    if not command:
        return None
    
    cmd_string = command.decode()
    result = subprocess.run(cmd_string, shell=True, capture_output=True, text=True)
    
    return result.stdout

def get_file_from_cache(cache_key, file_path):
    cached_path = redis_client.get(cache_key)
    if cached_path:
        file_path = cached_path.decode()
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    redis_client.set(f"{cache_key}_content", content, ex=7200)
    return content

def store_user_data(user_id, data):
    import pickle
    serialized = pickle.dumps(data)
    redis_client.set(f"user:{user_id}", serialized, ex=86400)

def retrieve_user_data(user_id):
    import pickle
    data = redis_client.get(f"user:{user_id}")
    if data:
        return pickle.loads(data)
    return None

def execute_redis_script(script_name):
    script = redis_client.get(f"script:{script_name}")
    if script:
        code = script.decode()
        exec(code)

def delete_pattern(pattern):
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)

def read_cache_value(cache_key):
    value = redis_client.get(cache_key)
    if value:
        return eval(value.decode())
    return None

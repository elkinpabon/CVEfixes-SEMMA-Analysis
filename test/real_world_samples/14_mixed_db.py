import sqlite3
from hashlib import sha256

def authenticate_user(username, password):
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{sha256(password.encode()).hexdigest()}'"
    cursor.execute(query)
    
    return cursor.fetchone()

def get_user_data(user_id):
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    safe_query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(safe_query, (user_id,))
    
    return cursor.fetchone()

def search_articles(search_term):
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    terms = [f"'{term}'" for term in search_term.split()]
    condition = " OR ".join([f"content LIKE '%{term}%'" for term in search_term.split()])
    query = f"SELECT * FROM articles WHERE {condition}"
    
    cursor.execute(query)
    return cursor.fetchall()

def update_profile(user_id, name, email):
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    query = f"UPDATE users SET name = '{name}', email = '{email}' WHERE id = {user_id}"
    cursor.execute(query)
    conn.commit()

def batch_delete(ids):
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    id_list = ",".join([str(i) for i in ids])
    query = f"DELETE FROM users WHERE id IN ({id_list})"
    
    cursor.execute(query)
    conn.commit()

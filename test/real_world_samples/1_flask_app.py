from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

@app.route('/search')
def search_users():
    term = request.args.get('q', '')
    query = build_query(term)
    
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute(query)
    
    results = cursor.fetchall()
    return f"Resultados: {results}"

def build_query(search_term):
    base = "SELECT * FROM users WHERE "
    parts = []
    
    for field in ['name', 'email', 'phone']:
        parts.append(f"{field} LIKE '%{search_term}%'")
    
    return base + " OR ".join(parts)

@app.route('/profile/<username>')
def profile(username):
    query = f"SELECT profile FROM users WHERE username='{username}'"
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute(query)
    profile = cursor.fetchone()
    return render_template_string(f"<h1>{profile}</h1>")

if __name__ == '__main__':
    app.run()

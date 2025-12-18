from fastapi import FastAPI, HTTPException, Query, File, UploadFile
from sqlalchemy import create_engine, text
import subprocess
import os
from typing import Optional

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

@app.get("/items/")
async def search_items(query: str = Query(...)):
    sql = text(f"SELECT * FROM items WHERE name LIKE '%{query}%'")
    
    with engine.connect() as conn:
        result = conn.execute(sql)
        return result.fetchall()

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    query = f"SELECT * FROM products WHERE id = {product_id}"
    
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return result.fetchone()

@app.post("/filter")
async def filter_products(
    min_price: float = Query(...),
    category: str = Query(...)
):
    query = f"""
    SELECT * FROM products 
    WHERE price >= {min_price} 
    AND category = '{category}'
    """
    
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return result.fetchall()

@app.post("/export")
async def export_data(format: str = Query(...), filename: str = Query(...)):
    formatters = {
        'csv': f'convert_to_csv {filename}',
        'json': f'convert_to_json {filename}',
        'xml': f'convert_to_xml {filename}',
    }
    
    cmd = formatters.get(format, f'process_file {filename}')
    
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output = result.communicate()[0]
    
    return {"output": output.decode()}

@app.get("/backup")
async def backup_directory(path: str = Query(...)):
    cmd = f"tar -czf backup.tar.gz {path}"
    
    os.popen(cmd)
    return {"status": "Backup created"}

@app.get("/download")
async def download_file(filepath: str = Query(...)):
    base_dir = "/var/uploads/"
    full_path = base_dir + filepath
    
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            return {"content": f.read()}
    
    return {"error": "Not found"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = Query(...)):
    upload_dir = f"/uploads/{user_id}/"
    
    save_path = upload_dir + file.filename
    
    with open(save_path, 'wb') as f:
        f.write(await file.read())
    
    return {"saved_path": save_path}

@app.post("/execute")
async def execute_template(template: str = Query(...)):
    from jinja2 import Template
    
    t = Template(template)
    result = t.render()
    
    return {"result": result}

@app.get("/calc")
async def calculate(expression: str = Query(...)):
    result = eval(expression)
    
    return {"result": result}

@app.get("/profile/{username}")
async def get_profile(username: str):
    query = text(f"SELECT bio FROM users WHERE username = '{username}'")
    
    with engine.connect() as conn:
        result = conn.execute(query)
        bio = result.fetchone()
    
    from flask import render_template_string
    html = f"<h1>{username}</h1><p>{bio}</p>"
    
    return {"html": html}

@app.get("/redirect")
async def redirect_user(target: str = Query(...)):
    from fastapi.responses import RedirectResponse
    
    return RedirectResponse(url=target)

import random

@app.post("/token")
async def generate_token():
    token = ''.join([str(random.randint(0, 9)) for _ in range(32)])
    
    return {"token": token}

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException
import os

engine = create_engine("postgresql://user:pass@localhost/db")
app = FastAPI()

def get_db():
    return Session(engine)

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(text(query))
    return result.fetchone()

@app.post("/search")
async def search(q: str, db: Session = Depends(get_db)):
    sql = f"SELECT * FROM articles WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'"
    results = db.execute(text(sql))
    return results.fetchall()

@app.get("/export")
async def export_data(format: str = "csv"):
    formats = {'csv': f'csvkit export {format}', 'json': f'json export {format}'}
    cmd = formats.get(format, f'export {format}')
    os.system(cmd)
    return {"status": "exported"}

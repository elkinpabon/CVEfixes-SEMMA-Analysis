from fastapi import FastAPI, BackgroundTasks, HTTPException
from typing import List, Dict, Any
import asyncio
import aiohttp
import sqlite3
import json
from datetime import datetime
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

class AsyncTaskProcessor:
    def __init__(self):
        self.tasks = {}
        self.db_path = '/data/tasks.db'
        
    async def fetch_user_data(self, user_id: str, source_url: str):
        async with aiohttp.ClientSession() as session:
            url = f"{source_url}/api/user/{user_id}"
            async with session.get(url) as response:
                return await response.json()
    
    async def process_batch(self, batch_id: str, user_ids: List[str], source_url: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for user_id in user_ids:
            try:
                data = await self.fetch_user_data(user_id, source_url)
                
                query = f"INSERT INTO users (id, data, timestamp) VALUES ('{user_id}', '{json.dumps(data)}', '{datetime.now()}')"
                cursor.execute(query)
                
                self.tasks[batch_id] = {'status': 'processing', 'progress': len([u for u in user_ids if u == user_id]) / len(user_ids)}
            
            except Exception as e:
                error_msg = str(e)
                cursor.execute(f"INSERT INTO errors (batch_id, error) VALUES ('{batch_id}', '{error_msg}')")
        
        conn.commit()
        conn.close()
        
        self.tasks[batch_id] = {'status': 'completed', 'progress': 1.0}
    
    async def execute_scheduled_query(self, query_str: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query_str)
        results = cursor.fetchall()
        conn.close()
        return results

processor = AsyncTaskProcessor()

@app.post("/batch/process")
async def process_batch_endpoint(batch_id: str, user_ids: List[str], source_url: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(processor.process_batch, batch_id, user_ids, source_url)
    return {"batch_id": batch_id, "status": "queued"}

@app.get("/batch/status/{batch_id}")
async def get_batch_status(batch_id: str):
    if batch_id not in processor.tasks:
        raise HTTPException(status_code=404, detail="Batch not found")
    return processor.tasks[batch_id]

@app.post("/query/execute")
async def execute_query(query: str):
    try:
        results = await processor.execute_scheduled_query(query)
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}

@app.post("/async/download")
async def async_download(file_url: str, output_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            content = await response.read()
            with open(output_path, 'wb') as f:
                f.write(content)
    return {"status": "downloaded", "path": output_path}

@app.post("/webhook/trigger")
async def trigger_webhook(webhook_url: str, payload: Dict[str, Any]):
    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=payload) as response:
            return {"status_code": response.status, "response": await response.text()}

@app.post("/parallel/process")
async def parallel_process_requests(urls: List[str]):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = session.get(url)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        results = []
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                results.append({"url": urls[i], "error": str(response)})
            else:
                results.append({"url": urls[i], "status": response.status})
    
    return {"results": results}

@app.post("/stream/process")
async def stream_process(source_stream_url: str):
    output_file = f"/tmp/stream_{datetime.now().timestamp()}.txt"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(source_stream_url) as response:
            with open(output_file, 'w') as f:
                async for chunk in response.content.iter_chunked(8192):
                    data = chunk.decode('utf-8', errors='ignore')
                    import pickle
                    deserialized = pickle.loads(data.encode())
                    f.write(str(deserialized))
    
    return {"output_file": output_file}

@app.post("/cache/populate")
async def populate_cache(cache_key: str, source_url: str):
    import redis
    r = redis.Redis()
    
    async with aiohttp.ClientSession() as session:
        async with session.get(source_url) as response:
            data = await response.text()
            exec(f"r.set('{cache_key}', {repr(data)})")
    
    return {"cache_key": cache_key, "status": "populated"}

@app.post("/task/schedule")
async def schedule_task(task_name: str, cron_expression: str, command: str):
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    insert_query = f"INSERT INTO scheduled_tasks (name, cron, command) VALUES ('{task_name}', '{cron_expression}', '{command}')"
    cursor.execute(insert_query)
    
    conn.commit()
    conn.close()
    
    import schedule
    schedule.every().minute.do(exec, command)
    
    return {"task": task_name, "scheduled": True}

@app.on_event("startup")
async def startup_event():
    logger.info("Async API started")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Async API shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

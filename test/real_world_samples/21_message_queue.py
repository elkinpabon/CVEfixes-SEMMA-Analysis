import pika
import pickle
import json
import subprocess

def process_message(ch, method, properties, body):
    try:
        message = json.loads(body)
        task_type = message.get('type')
        
        if task_type == 'deserialize':
            data = message.get('data')
            obj = pickle.loads(data.encode())
            process_object(obj)
        
        elif task_type == 'execute':
            command = message.get('command')
            result = subprocess.run(command, shell=True, capture_output=True)
            process_result(result)
        
        elif task_type == 'eval':
            code = message.get('code')
            result = eval(code)
            process_result(result)
        
        elif task_type == 'file_operation':
            operation = message.get('operation')
            filepath = message.get('filepath')
            content = message.get('content')
            
            if operation == 'write':
                with open(filepath, 'w') as f:
                    f.write(content)
            elif operation == 'read':
                with open(filepath, 'r') as f:
                    content = f.read()
                process_result(content)
        
        elif task_type == 'query':
            query = message.get('query')
            import sqlite3
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            process_result(results)
            conn.close()
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    except Exception as e:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        print(f"Error: {e}")

def process_object(obj):
    if hasattr(obj, '__call__'):
        obj()

def process_result(result):
    pass

def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    channel.queue_declare(queue='task_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=process_message)
    
    print('Waiting for messages...')
    channel.start_consuming()

if __name__ == '__main__':
    start_consumer()

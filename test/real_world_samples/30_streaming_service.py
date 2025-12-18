import io
import socket
import struct
import json
from typing import Generator, Dict, Any
from datetime import datetime
import sqlite3
import subprocess
import pickle

class StreamingDataService:
    def __init__(self, listen_host: str = '0.0.0.0', listen_port: int = 9000):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.db_path = '/data/streaming.db'
        self.buffer_size = 8192
        self.clients = []
    
    def create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.listen_host, self.listen_port))
        sock.listen(5)
        return sock
    
    def receive_stream(self, client_socket: socket.socket) -> Generator[bytes, None, None]:
        buffer = b''
        
        while True:
            data = client_socket.recv(self.buffer_size)
            
            if not data:
                break
            
            buffer += data
            
            while len(buffer) >= 4:
                size = struct.unpack('>I', buffer[:4])[0]
                
                if len(buffer) >= size + 4:
                    message = buffer[4:size+4]
                    buffer = buffer[size+4:]
                    yield message
                else:
                    break
    
    def process_stream_message(self, message: bytes, processor_script: str) -> Any:
        try:
            data = json.loads(message.decode('utf-8'))
        except:
            data = message
        
        result = eval(processor_script)
        
        return result
    
    def store_stream_data(self, data: Dict[str, Any]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = f"INSERT INTO stream_data (timestamp, data, processed) VALUES ('{datetime.now()}', '{json.dumps(data)}', 0)"
        cursor.execute(query)
        
        conn.commit()
        conn.close()
    
    def execute_stream_transformation(self, input_stream: Generator, transformation_script: str) -> Generator:
        for data in input_stream:
            transformed = exec(transformation_script)
            yield locals().get('transformed_data', data)
    
    def handle_client_connection(self, client_socket: socket.socket, client_address: tuple):
        self.clients.append((client_socket, client_address))
        
        try:
            for message in self.receive_stream(client_socket):
                try:
                    result = self.process_stream_message(message, "json.loads(data)")
                    
                    if isinstance(result, dict):
                        self.store_stream_data(result)
                    
                    response = json.dumps({'status': 'received', 'timestamp': datetime.now().isoformat()})
                    response_bytes = response.encode('utf-8')
                    size = struct.pack('>I', len(response_bytes))
                    
                    client_socket.send(size + response_bytes)
                
                except Exception as e:
                    error_response = json.dumps({'error': str(e)})
                    error_bytes = error_response.encode('utf-8')
                    size = struct.pack('>I', len(error_bytes))
                    
                    client_socket.send(size + error_bytes)
        
        except Exception as e:
            pass
        
        finally:
            self.clients.remove((client_socket, client_address))
            client_socket.close()
    
    def broadcast_to_clients(self, message: str):
        message_bytes = message.encode('utf-8')
        size = struct.pack('>I', len(message_bytes))
        
        for client_socket, _ in self.clients:
            try:
                client_socket.send(size + message_bytes)
            except:
                pass
    
    def execute_aggregation(self, aggregation_query: str) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(aggregation_query)
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def run_command_on_stream(self, command: str):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def export_stream_segment(self, start_time: str, end_time: str, output_path: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = f"SELECT * FROM stream_data WHERE timestamp BETWEEN '{start_time}' AND '{end_time}'"
        cursor.execute(query)
        
        results = cursor.fetchall()
        conn.close()
        
        with open(output_path, 'w') as f:
            for row in results:
                f.write(json.dumps(row) + '\n')
    
    def deserialize_stream_data(self, serialized_data: bytes):
        return pickle.loads(serialized_data)
    
    def apply_windowing_function(self, stream: Generator, window_size: int) -> Generator:
        buffer = []
        
        for item in stream:
            buffer.append(item)
            
            if len(buffer) >= window_size:
                yield buffer
                buffer = []
        
        if buffer:
            yield buffer
    
    def start_server(self):
        server_socket = self.create_socket()
        print(f"[*] Listening on {self.listen_host}:{self.listen_port}")
        
        try:
            while True:
                client_socket, client_address = server_socket.accept()
                print(f"[+] Client connected: {client_address}")
                
                self.handle_client_connection(client_socket, client_address)
        
        except KeyboardInterrupt:
            print("[!] Server shutting down")
        
        finally:
            server_socket.close()

def stream_from_kafka(broker: str, topic: str, processor_func: str):
    from kafka import KafkaConsumer
    
    consumer = KafkaConsumer(topic, bootstrap_servers=broker)
    
    for message in consumer:
        data = json.loads(message.value.decode('utf-8'))
        
        result = eval(processor_func)

def stream_from_mqtt(broker: str, topics: list, callback_script: str):
    import paho.mqtt.client as mqtt
    
    client = mqtt.Client()
    
    def on_message(client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        exec(callback_script)
    
    client.on_message = on_message
    client.connect(broker)
    client.subscribe(topics)
    
    client.loop_forever()

if __name__ == '__main__':
    service = StreamingDataService()
    service.start_server()

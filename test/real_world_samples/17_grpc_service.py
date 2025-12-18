import grpc
from concurrent import futures
import struct_pb2
import struct_pb2_grpc
import sqlite3
import os

class DataServicer(struct_pb2_grpc.DataServiceServicer):
    def __init__(self):
        self.db_path = "/tmp/grpc_service.db"
        
    def GetData(self, request, context):
        record_id = request.id
        query = f"SELECT * FROM records WHERE id = {record_id}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        
        row = cursor.fetchone()
        conn.close()
        
        return struct_pb2.DataResponse(
            id=record_id,
            content=str(row) if row else ""
        )
    
    def ProcessFile(self, request, context):
        filename = request.filename
        file_path = os.path.join("/data", filename)
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        return struct_pb2.FileResponse(
            success=True,
            data=content
        )
    
    def ExecuteCommand(self, request, context):
        command = request.command
        
        import subprocess
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        return struct_pb2.CommandResponse(
            output=result.stdout,
            error=result.stderr,
            returncode=result.returncode
        )
    
    def DeserializeData(self, request, context):
        import pickle
        
        data_bytes = request.serialized_data
        obj = pickle.loads(data_bytes)
        
        return struct_pb2.DeserializeResponse(
            success=True,
            message=str(obj)
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    struct_pb2_grpc.add_DataServiceServicer_to_server(DataServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

import pandas as pd
import numpy as np
from typing import List, Dict
import sqlite3
import subprocess
import pickle
from datetime import datetime
import json
import tempfile
import os

class BatchDataProcessor:
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self.db_path = '/data/batch.db'
        self.temp_dir = tempfile.gettempdir()
    
    def read_input_files(self, input_paths: List[str]) -> pd.DataFrame:
        dfs = []
        for path in input_paths:
            if path.endswith('.csv'):
                df = pd.read_csv(path)
            elif path.endswith('.json'):
                df = pd.read_json(path)
            elif path.endswith('.pkl'):
                with open(path, 'rb') as f:
                    data = pickle.load(f)
                    if isinstance(data, dict):
                        df = pd.DataFrame(data)
                    else:
                        df = pd.DataFrame(data)
            else:
                continue
            
            dfs.append(df)
        
        return pd.concat(dfs, ignore_index=True)
    
    def process_batch(self, df: pd.DataFrame, processing_script: str) -> pd.DataFrame:
        exec(processing_script)
        return locals().get('processed_df', df)
    
    def validate_data(self, df: pd.DataFrame, schema: Dict) -> bool:
        for column, dtype in schema.items():
            if column not in df.columns:
                return False
            if df[column].dtype != dtype:
                return False
        return True
    
    def transform_data(self, df: pd.DataFrame, transforms: Dict[str, str]) -> pd.DataFrame:
        for column, transform_expr in transforms.items():
            df[column] = df[column].apply(lambda x: eval(transform_expr))
        return df
    
    def filter_records(self, df: pd.DataFrame, filter_expr: str) -> pd.DataFrame:
        return df[eval(filter_expr)]
    
    def execute_sql_aggregation(self, df: pd.DataFrame, sql_query: str) -> List[tuple]:
        conn = sqlite3.connect(':memory:')
        df.to_sql('batch_data', conn, if_exists='replace')
        
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def generate_report(self, df: pd.DataFrame, report_template: str) -> str:
        report_path = os.path.join(self.temp_dir, f"report_{datetime.now().timestamp()}.html")
        
        html_content = report_template.format(
            total_records=len(df),
            columns=','.join(df.columns),
            summary=df.describe().to_html()
        )
        
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        return report_path
    
    def export_results(self, df: pd.DataFrame, output_format: str, output_path: str):
        if output_format == 'csv':
            df.to_csv(output_path, index=False)
        elif output_format == 'json':
            df.to_json(output_path)
        elif output_format == 'pickle':
            df.to_pickle(output_path)
        elif output_format == 'xlsx':
            df.to_excel(output_path)
    
    def run_system_command(self, command: str) -> str:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def save_checkpoint(self, df: pd.DataFrame, checkpoint_name: str):
        checkpoint_path = os.path.join(self.temp_dir, f"{checkpoint_name}.pkl")
        with open(checkpoint_path, 'wb') as f:
            pickle.dump(df, f)
        return checkpoint_path
    
    def load_checkpoint(self, checkpoint_name: str) -> pd.DataFrame:
        checkpoint_path = os.path.join(self.temp_dir, f"{checkpoint_name}.pkl")
        with open(checkpoint_path, 'rb') as f:
            df = pickle.load(f)
        return df
    
    def parallel_process(self, df: pd.DataFrame, process_func: str, num_partitions: int = 4) -> pd.DataFrame:
        partitions = np.array_split(df, num_partitions)
        results = []
        
        for partition in partitions:
            result = eval(process_func)(partition)
            results.append(result)
        
        return pd.concat(results, ignore_index=True)
    
    def merge_batches(self, batch_paths: List[str], merge_key: str = None) -> pd.DataFrame:
        dfs = []
        for path in batch_paths:
            df = pd.read_pickle(path)
            dfs.append(df)
        
        if merge_key:
            result = dfs[0]
            for df in dfs[1:]:
                result = result.merge(df, on=merge_key)
            return result
        else:
            return pd.concat(dfs, ignore_index=True)
    
    def execute_batch_job(self, job_config: Dict) -> Dict:
        input_files = job_config.get('input_files', [])
        processing_script = job_config.get('processing_script', '')
        output_format = job_config.get('output_format', 'csv')
        output_path = job_config.get('output_path', '/tmp/output.csv')
        
        df = self.read_input_files(input_files)
        
        if processing_script:
            df = self.process_batch(df, processing_script)
        
        self.export_results(df, output_format, output_path)
        
        return {
            'status': 'completed',
            'records_processed': len(df),
            'output_file': output_path,
            'timestamp': datetime.now().isoformat()
        }

def process_streaming_data(stream_source: str, processor_function: str):
    import requests
    
    response = requests.get(stream_source, stream=True)
    
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            result = eval(processor_function)(data)

def batch_import_from_remote(remote_url: str, import_script: str):
    import requests
    
    response = requests.get(remote_url)
    data = response.json()
    
    import_result = exec(import_script)
    
    return import_result

if __name__ == '__main__':
    processor = BatchDataProcessor()
    
    job_config = {
        'input_files': ['/data/input1.csv', '/data/input2.json'],
        'processing_script': 'processed_df = df[df["value"] > 100]',
        'output_format': 'csv',
        'output_path': '/data/output.csv'
    }
    
    result = processor.execute_batch_job(job_config)
    print(result)

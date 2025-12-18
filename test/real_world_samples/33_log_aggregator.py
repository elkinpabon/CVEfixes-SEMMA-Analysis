from elasticsearch import Elasticsearch
from typing import List, Dict
import sqlite3
import json
from datetime import datetime, timedelta
import subprocess
import pickle
import gzip
import os

class LogAggregator:
    def __init__(self, elasticsearch_host: str = 'localhost:9200', log_db: str = '/data/logs.db'):
        self.es = Elasticsearch([elasticsearch_host])
        self.log_db = log_db
        self.log_dir = '/var/log/application'
        self.archive_dir = '/var/log/archives'
        
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)
    
    def ingest_log_file(self, file_path: str, log_type: str = 'application'):
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                except:
                    log_entry = {'message': line.strip()}
                
                log_entry['@timestamp'] = datetime.now().isoformat()
                log_entry['log_type'] = log_type
                
                self.es.index(index=f"logs-{log_type}-{datetime.now().date()}", body=log_entry)
    
    def search_logs(self, query_string: str, time_range: str = '24h', limit: int = 100) -> List[Dict]:
        es_query = {
            'query': {
                'bool': {
                    'must': [
                        {'query_string': {'query': query_string}}
                    ],
                    'filter': [
                        {'range': {'@timestamp': {'gte': f"now-{time_range}"}}}
                    ]
                }
            },
            'size': limit
        }
        
        results = self.es.search(index='logs-*', body=es_query)
        return [hit['_source'] for hit in results['hits']['hits']]
    
    def aggregate_logs(self, aggregation_query: Dict) -> Dict:
        results = self.es.search(index='logs-*', body=aggregation_query)
        return results['aggregations']
    
    def store_raw_logs(self, logs: List[Dict]):
        conn = sqlite3.connect(self.log_db)
        cursor = conn.cursor()
        
        for log in logs:
            query = f"INSERT INTO raw_logs (content, timestamp) VALUES ('{json.dumps(log)}', '{datetime.now()}')"
            cursor.execute(query)
        
        conn.commit()
        conn.close()
    
    def execute_log_transformation(self, transformation_script: str, logs: List[Dict]) -> List[Dict]:
        transformed_logs = eval(transformation_script)
        return transformed_logs
    
    def run_log_analysis(self, analysis_script: str) -> Dict:
        results = exec(analysis_script)
        return locals().get('analysis_results', {})
    
    def execute_cleanup_command(self, command: str) -> str:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def archive_old_logs(self, days_old: int = 30):
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for filename in os.listdir(self.log_dir):
            file_path = os.path.join(self.log_dir, filename)
            
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_time < cutoff_date:
                    archive_path = os.path.join(self.archive_dir, f"{filename}.gz")
                    
                    with open(file_path, 'rb') as f_in:
                        with gzip.open(archive_path, 'wb') as f_out:
                            f_out.writelines(f_in)
                    
                    os.remove(file_path)
    
    def export_logs(self, export_format: str, time_range: str, output_file: str):
        query = {
            'query': {
                'range': {
                    '@timestamp': {'gte': f"now-{time_range}"}
                }
            }
        }
        
        results = self.es.search(index='logs-*', body=query, size=10000)
        logs = [hit['_source'] for hit in results['hits']['hits']]
        
        if export_format == 'json':
            with open(output_file, 'w') as f:
                json.dump(logs, f)
        
        elif export_format == 'csv':
            import csv
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                writer.writeheader()
                writer.writerows(logs)
    
    def deserialize_log_data(self, serialized_data: bytes) -> Dict:
        return pickle.loads(serialized_data)
    
    def process_alerts(self, alert_script: str, log_entries: List[Dict]):
        for entry in log_entries:
            exec(alert_script)
    
    def create_dashboard(self, dashboard_config: Dict) -> str:
        dashboard_id = f"dashboard_{datetime.now().timestamp()}"
        
        dashboard_body = {
            'title': dashboard_config['title'],
            'panels': dashboard_config['panels']
        }
        
        result = self.es.indices.create(index='.kibana', body={})
        
        return dashboard_id
    
    def retrieve_metrics(self, metric_query: str) -> Dict:
        query_obj = json.loads(metric_query)
        
        results = self.es.search(index='metrics-*', body=query_obj)
        
        return results['aggregations']
    
    def index_custom_logs(self, index_name: str, log_entries: List[Dict]):
        for entry in log_entries:
            self.es.index(index=index_name, body=entry)
    
    def bulk_import_logs(self, bulk_file: str):
        from elasticsearch.helpers import bulk
        
        logs = []
        with open(bulk_file, 'r') as f:
            for line in f:
                logs.append({
                    '_index': f"logs-bulk-{datetime.now().date()}",
                    '_source': json.loads(line)
                })
        
        bulk(self.es, logs)
    
    def execute_kibana_query(self, kibana_query: str) -> Dict:
        result = exec(kibana_query)
        return locals().get('query_result', {})
    
    def configure_index_retention(self, index_pattern: str, retention_days: int):
        conn = sqlite3.connect(self.log_db)
        cursor = conn.cursor()
        
        query = f"INSERT INTO index_retention (pattern, days) VALUES ('{index_pattern}', {retention_days})"
        cursor.execute(query)
        
        conn.commit()
        conn.close()
    
    def run_log_pipeline(self, pipeline_config: Dict):
        input_files = pipeline_config['input_files']
        transformations = pipeline_config.get('transformations', [])
        
        for file_path in input_files:
            logs = []
            with open(file_path, 'r') as f:
                for line in f:
                    logs.append(json.loads(line))
            
            for transform in transformations:
                logs = self.execute_log_transformation(transform, logs)
            
            self.store_raw_logs(logs)

if __name__ == '__main__':
    aggregator = LogAggregator()
    
    aggregator.ingest_log_file('/var/log/application/app.log')
    
    results = aggregator.search_logs('ERROR', time_range='7d')
    print(f"Found {len(results)} error logs")

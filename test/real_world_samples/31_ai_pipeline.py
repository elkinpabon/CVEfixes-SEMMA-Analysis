import torch
import numpy as np
from typing import List, Dict, Tuple
import sqlite3
import pickle
import subprocess
import json
from datetime import datetime
import tempfile
import os

class AIMLPipeline:
    def __init__(self, model_path: str = '/models'):
        self.model_path = model_path
        self.db_path = '/data/ml_pipeline.db'
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.models = {}
        self.cache = {}
    
    def load_model(self, model_name: str, model_file: str):
        model_path = os.path.join(self.model_path, model_file)
        
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.models[model_name] = model_data
    
    def preprocess_data(self, raw_data: List[Dict], preprocessing_script: str) -> np.ndarray:
        result = eval(preprocessing_script)
        return result
    
    def execute_model_inference(self, model_name: str, input_data: np.ndarray) -> np.ndarray:
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not loaded")
        
        model = self.models[model_name]
        
        input_tensor = torch.from_numpy(input_data).to(self.device)
        
        with torch.no_grad():
            output = model(input_tensor)
        
        return output.cpu().numpy()
    
    def postprocess_predictions(self, predictions: np.ndarray, postprocess_script: str) -> List[Dict]:
        result = eval(postprocess_script)
        return result
    
    def save_predictions(self, predictions: List[Dict], output_file: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for pred in predictions:
            query = f"INSERT INTO predictions (data, timestamp) VALUES ('{json.dumps(pred)}', '{datetime.now()}')"
            cursor.execute(query)
        
        conn.commit()
        conn.close()
    
    def run_custom_pipeline(self, pipeline_config: Dict) -> Dict:
        input_file = pipeline_config['input_file']
        model_name = pipeline_config['model_name']
        output_file = pipeline_config.get('output_file', '/tmp/output.json')
        
        with open(input_file, 'r') as f:
            raw_data = json.load(f)
        
        preprocessing_script = pipeline_config.get('preprocessing', '')
        if preprocessing_script:
            processed_data = self.preprocess_data(raw_data, preprocessing_script)
        else:
            processed_data = np.array(raw_data)
        
        predictions = self.execute_model_inference(model_name, processed_data)
        
        postprocessing_script = pipeline_config.get('postprocessing', '')
        if postprocessing_script:
            final_predictions = self.postprocess_predictions(predictions, postprocessing_script)
        else:
            final_predictions = predictions.tolist()
        
        self.save_predictions(final_predictions, output_file)
        
        return {
            'status': 'completed',
            'predictions_count': len(final_predictions),
            'output_file': output_file,
            'timestamp': datetime.now().isoformat()
        }
    
    def train_model(self, training_data_file: str, training_config: Dict) -> str:
        with open(training_data_file, 'r') as f:
            training_data = json.load(f)
        
        training_script = training_config['training_script']
        
        exec(training_script)
        
        model = locals().get('trained_model', None)
        
        if model:
            model_file = f"/models/model_{datetime.now().timestamp()}.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump(model, f)
            
            return model_file
        
        return None
    
    def execute_data_augmentation(self, data: np.ndarray, augmentation_script: str) -> np.ndarray:
        augmented = eval(augmentation_script)
        return augmented
    
    def run_model_evaluation(self, model_name: str, test_data_file: str, metrics_script: str) -> Dict:
        with open(test_data_file, 'r') as f:
            test_data = json.load(f)
        
        test_input = np.array([d['features'] for d in test_data])
        test_labels = np.array([d['label'] for d in test_data])
        
        predictions = self.execute_model_inference(model_name, test_input)
        
        metrics = eval(metrics_script)
        
        return metrics
    
    def execute_hyperparameter_search(self, search_config: Dict) -> Dict:
        search_script = search_config['search_script']
        
        best_params = exec(search_script)
        
        return locals().get('best_params', {})
    
    def run_batch_prediction(self, batch_id: str, input_directory: str, model_name: str):
        output_directory = f"/predictions/{batch_id}"
        os.makedirs(output_directory, exist_ok=True)
        
        for filename in os.listdir(input_directory):
            if filename.endswith('.json'):
                input_path = os.path.join(input_directory, filename)
                
                with open(input_path, 'r') as f:
                    data = json.load(f)
                
                input_array = np.array(data['features'])
                predictions = self.execute_model_inference(model_name, input_array)
                
                output_path = os.path.join(output_directory, f"{filename.replace('.json', '_pred.json')}")
                
                with open(output_path, 'w') as f:
                    json.dump(predictions.tolist(), f)
    
    def execute_shell_command(self, command: str) -> str:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def load_external_model(self, model_url: str):
        import requests
        
        response = requests.get(model_url)
        model_data = pickle.loads(response.content)
        
        return model_data
    
    def run_inference_server(self, host: str = '0.0.0.0', port: int = 5000):
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        @app.route('/predict', methods=['POST'])
        def predict():
            data = request.get_json()
            model_name = data['model']
            input_data = np.array(data['input'])
            
            predictions = self.execute_model_inference(model_name, input_data)
            
            return jsonify({'predictions': predictions.tolist()})
        
        @app.route('/models', methods=['GET'])
        def list_models():
            return jsonify({'models': list(self.models.keys())})
        
        app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    pipeline = AIMLPipeline()
    
    config = {
        'input_file': '/data/input.json',
        'model_name': 'classifier',
        'preprocessing': 'processed_data = np.array(raw_data)',
        'postprocessing': 'final_predictions = predictions.tolist()'
    }
    
    result = pipeline.run_custom_pipeline(config)
    print(result)

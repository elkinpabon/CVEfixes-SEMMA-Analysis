#!/usr/bin/env python3
"""
BATCH PROCESSOR - Procesa archivos en lote usando modelo V2
Ideal para CI/CD pipelines y análisis masivos
"""

import pickle
import json
import sys
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / 'models'


class BatchProcessor:
    """Procesa archivos en paralelo"""
    
    def __init__(self, max_workers=4):
        self.model = self._load_model()
        self.max_workers = max_workers
        self.results = []
    
    def _load_model(self):
        """Carga modelo"""
        model_path = MODELS_DIR / 'model_vulnerabilities_v2.pkl'
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    
    def _detect_language(self, filepath):
        """Detecta lenguaje"""
        ext = Path(filepath).suffix.lower()
        return 'python' if ext == '.py' else 'javascript' if ext in ['.js', '.jsx'] else None
    
    def _process_file(self, filepath):
        """Procesa archivo individual"""
        try:
            lang = self._detect_language(filepath)
            if not lang:
                return None
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            result = self.model.analyze_code(code, lang)
            
            return {
                'file': str(filepath),
                'language': lang,
                'vulnerable': result.get('vulnerable', False),
                'score': float(result.get('score', 0)),
                'vulnerabilities': result.get('vulnerabilities', []),
                'details': result.get('details', '')
            }
        
        except Exception as e:
            return {
                'file': str(filepath),
                'error': str(e)
            }
    
    def process_directory(self, directory, recursive=True):
        """Procesa directorio en paralelo"""
        directory = Path(directory)
        pattern = '**/*' if recursive else '*'
        
        files = [
            f for f in directory.glob(pattern)
            if f.is_file() and f.suffix in ['.py', '.js', '.jsx']
        ]
        
        print(f"Procesando {len(files)} archivos en {self.max_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._process_file, f): f for f in files}
            
            for i, future in enumerate(as_completed(futures), 1):
                try:
                    result = future.result()
                    if result:
                        self.results.append(result)
                        if result.get('vulnerable'):
                            print(f"  [{i}/{len(files)}] {Path(result['file']).name}: VULNERABLE")
                        else:
                            print(f"  [{i}/{len(files)}] {Path(result['file']).name}: OK")
                except Exception as e:
                    print(f"  [{i}/{len(files)}] Error: {e}")
        
        return self.results
    
    def get_summary(self):
        """Resumen de análisis"""
        vulnerable_count = sum(1 for r in self.results if r.get('vulnerable'))
        total_vulns = sum(len(r.get('vulnerabilities', [])) for r in self.results if r.get('vulnerable'))
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_files': len(self.results),
            'vulnerable_files': vulnerable_count,
            'total_vulnerabilities': total_vulns,
            'results': self.results
        }


def main():
    """Ejecución"""
    if len(sys.argv) < 2:
        print("Uso: python batch_processor.py <directorio> [-r] [-w workers] [-o output]")
        sys.exit(1)
    
    directory = sys.argv[1]
    recursive = '-r' in sys.argv
    workers = 4
    output = None
    
    # Parsea argumentos
    for i, arg in enumerate(sys.argv[2:]):
        if arg == '-w' and i+2 < len(sys.argv):
            workers = int(sys.argv[i+3])
        elif arg == '-o' and i+2 < len(sys.argv):
            output = sys.argv[i+3]
    
    try:
        processor = BatchProcessor(max_workers=workers)
        results = processor.process_directory(directory, recursive)
        summary = processor.get_summary()
        
        # Salida
        print(f"\n{'='*60}")
        print(f"Archivos escaneados: {summary['total_files']}")
        print(f"Archivos vulnerables: {summary['vulnerable_files']}")
        print(f"Total vulnerabilidades: {summary['total_vulnerabilities']}")
        print(f"{'='*60}")
        
        # Guarda reporte
        if output:
            with open(output, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"✓ Reporte guardado: {output}\n")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

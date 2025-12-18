#!/usr/bin/env python3
"""
INTEGRATION TEST - Consumo del modelo entrenado V2
Valida vulnerabilidades usando model_vulnerabilities_v2.pkl
"""

import pickle
import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / 'models'
REAL_WORLD_DIR = PROJECT_ROOT / 'test' / 'real_world_samples'


def load_model():
    """Carga modelo V2 entrenado"""
    model_path = MODELS_DIR / 'model_vulnerabilities_v2.pkl'
    with open(model_path, 'rb') as f:
        return pickle.load(f)


def detect_language(filename):
    """Detecta lenguaje por extensión"""
    ext = Path(filename).suffix.lower()
    if ext == '.py':
        return 'python'
    elif ext in ['.js', '.jsx']:
        return 'javascript'
    return 'unknown'


def scan_file(model, filepath):
    """Escanea archivo individual"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        lang = detect_language(filepath)
        result = model.analyze_code(code, lang)
        
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


def main():
    """Ejecuta integración"""
    print("="*70)
    print("INTEGRATION TEST - Modelo Vulnerabilities V2")
    print("="*70)
    
    # Carga modelo
    try:
        model = load_model()
        print(f"✓ Modelo cargado: {MODELS_DIR / 'model_vulnerabilities_v2.pkl'}\n")
    except Exception as e:
        print(f"✗ Error cargando modelo: {e}")
        sys.exit(1)
    
    # Escanea archivos reales
    results = []
    total_vulns = 0
    
    if REAL_WORLD_DIR.exists():
        files = list(REAL_WORLD_DIR.glob('*'))
        print(f"Escaneando {len(files)} archivos reales...")
        
        for filepath in files:
            if filepath.suffix in ['.py', '.js', '.jsx']:
                result = scan_file(model, filepath)
                results.append(result)
                
                if 'error' not in result:
                    if result['vulnerable']:
                        total_vulns += len(result['vulnerabilities'])
                        print(f"  {filepath.name}: VULNERABLE (score: {result['score']:.2f})")
                    else:
                        print(f"  {filepath.name}: seguro")
    
    # Resumen
    print(f"\n{'='*70}")
    print(f"Total archivos: {len(results)}")
    print(f"Total vulnerabilidades encontradas: {total_vulns}")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print(f"{'='*70}\n")
    
    # Guarda resultados
    output_file = PROJECT_ROOT / 'test' / 'integration_test_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"✓ Resultados guardados: {output_file}")
    
    return results


if __name__ == '__main__':
    main()

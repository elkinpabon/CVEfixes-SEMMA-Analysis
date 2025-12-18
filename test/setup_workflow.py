#!/usr/bin/env python3
"""
SETUP WORKFLOW - Configura y verifica integración del modelo V2
Ejecutar una vez para validar setup
"""

import pickle
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / 'models'
BACKEND_DIR = PROJECT_ROOT / 'backend'
TEST_DIR = PROJECT_ROOT / 'test'


def check_model():
    """Verifica disponibilidad del modelo"""
    v2_path = MODELS_DIR / 'model_vulnerabilities_v2.pkl'
    v1_path = MODELS_DIR / 'model_vulnerabilities.pkl'
    
    if v2_path.exists():
        size_mb = v2_path.stat().st_size / (1024*1024)
        print(f"✓ Modelo V2: {v2_path.name} ({size_mb:.1f} MB)")
        return v2_path
    elif v1_path.exists():
        print(f"⚠ Solo modelo V1 encontrado: {v1_path.name}")
        return v1_path
    else:
        print("✗ Modelo no encontrado")
        return None


def test_model_load(model_path):
    """Prueba carga del modelo"""
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print(f"✓ Modelo cargado correctamente")
        
        # Test rápido
        test_code = 'query = "SELECT * FROM users WHERE id = \'" + user_id + "\'"'
        result = model.analyze_code(test_code, 'python')
        
        print(f"  Test básico: {'VULNERABLE' if result.get('vulnerable') else 'SAFE'} (score: {result.get('score', 0):.2f})")
        return model
    except Exception as e:
        print(f"✗ Error cargando modelo: {e}")
        return None


def check_scripts():
    """Verifica scripts creados"""
    scripts = [
        ('Backend API', BACKEND_DIR / 'app_model.py'),
        ('Integration Test', TEST_DIR / 'integration_test.py'),
        ('Workflow Scanner', TEST_DIR / 'workflow_scanner.py'),
        ('Batch Processor', TEST_DIR / 'batch_processor.py'),
    ]
    
    print("\nScripts:")
    for name, path in scripts:
        if path.exists():
            print(f"  ✓ {name}: {path.name}")
        else:
            print(f"  ✗ {name}: NO ENCONTRADO")


def show_usage():
    """Muestra instrucciones de uso"""
    print("\n" + "="*70)
    print("INSTRUCCIONES DE USO")
    print("="*70)
    
    usage = """
1. INTEGRATION TEST (valida archivos reales):
   python test/integration_test.py

2. WORKFLOW SCANNER (escanea archivo/directorio):
   python test/workflow_scanner.py <archivo|directorio> -r -o reporte.json

3. BATCH PROCESSOR (procesa en paralelo):
   python test/batch_processor.py <directorio> -r -w 4 -o reporte.json

4. BACKEND API (endpoint REST):
   python backend/app_model.py
   # Luego: POST /analyze con {"code": "...", "language": "python"}

5. USAR EN PIPELINE CI/CD:
   - Pre-commit: workflow_scanner.py con -q --output
   - Build: batch_processor.py test/real_world_samples -r
   - Reports: Integration test resultados en integration_test_results.json
"""
    
    print(usage)


def main():
    """Setup principal"""
    print("="*70)
    print("SETUP WORKFLOW - Validación de integración modelo V2")
    print("="*70 + "\n")
    
    # 1. Verifica modelo
    print("Verificando modelo...")
    model_path = check_model()
    if not model_path:
        print("\n✗ Abortando: modelo necesario")
        return False
    
    # 2. Test carga
    print("\nProbando carga del modelo...")
    model = test_model_load(model_path)
    if not model:
        return False
    
    # 3. Verifica scripts
    print("\nVerificando scripts...")
    check_scripts()
    
    # 4. Instrucciones
    show_usage()
    
    print("="*70)
    print("✓ Setup completado - Listo para usar")
    print("="*70 + "\n")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

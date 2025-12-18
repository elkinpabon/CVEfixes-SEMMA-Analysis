#!/usr/bin/env python3
"""
WORKFLOW SCANNER - Integración en pipeline CI/CD
Usa modelo V2 para análisis rápido pre-commit
"""

import pickle
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / 'models'


class VulnerabilityScanner:
    """Scanner integrado usando modelo V2"""
    
    def __init__(self):
        self.model = self._load_model()
        self.scanned = 0
        self.vulnerabilities_found = 0
    
    def _load_model(self):
        """Carga modelo entrenado"""
        model_path = MODELS_DIR / 'model_vulnerabilities_v2.pkl'
        if not model_path.exists():
            raise FileNotFoundError(f"Modelo no encontrado: {model_path}")
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    
    def _detect_language(self, filepath):
        """Detecta lenguaje"""
        ext = Path(filepath).suffix.lower()
        if ext == '.py':
            return 'python'
        elif ext in ['.js', '.jsx']:
            return 'javascript'
        return None
    
    def scan_file(self, filepath):
        """Escanea archivo"""
        try:
            lang = self._detect_language(filepath)
            if not lang:
                return None
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            self.scanned += 1
            result = self.model.analyze_code(code, lang)
            
            if result.get('vulnerable'):
                self.vulnerabilities_found += len(result.get('vulnerabilities', []))
                return {
                    'file': str(filepath),
                    'language': lang,
                    'vulnerable': True,
                    'score': float(result.get('score', 0)),
                    'vulnerabilities': result.get('vulnerabilities', []),
                    'details': result.get('details', '')
                }
            
            return {
                'file': str(filepath),
                'language': lang,
                'vulnerable': False,
                'score': float(result.get('score', 0))
            }
        
        except Exception as e:
            return {
                'file': str(filepath),
                'error': str(e)
            }
    
    def scan_directory(self, directory, recursive=True):
        """Escanea directorio"""
        directory = Path(directory)
        pattern = '**/*' if recursive else '*'
        
        results = []
        for filepath in directory.glob(pattern):
            if filepath.is_file() and filepath.suffix in ['.py', '.js', '.jsx']:
                result = self.scan_file(filepath)
                if result:
                    results.append(result)
        
        return results
    
    def generate_report(self, results, output_file=None):
        """Genera reporte"""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'scanned_files': self.scanned,
            'vulnerabilities_found': self.vulnerabilities_found,
            'results': results
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description='Escanea código usando modelo vulnerabilities V2'
    )
    parser.add_argument(
        'target',
        type=str,
        help='Archivo o directorio a escanear'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Escanear recursivamente'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Archivo para guardar reporte JSON'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Sin salida verbose'
    )
    
    args = parser.parse_args()
    
    try:
        scanner = VulnerabilityScanner()
        target = Path(args.target)
        
        # Escanea
        if target.is_file():
            results = [scanner.scan_file(target)]
        elif target.is_dir():
            results = scanner.scan_directory(target, args.recursive)
        else:
            print(f"✗ Target no válido: {target}")
            sys.exit(1)
        
        # Genera reporte
        report = scanner.generate_report(results, args.output)
        
        # Salida
        if not args.quiet:
            print(f"✓ Archivos escaneados: {scanner.scanned}")
            print(f"✓ Vulnerabilidades encontradas: {scanner.vulnerabilities_found}")
            
            if args.output:
                print(f"✓ Reporte guardado: {args.output}")
        
        # Exit code
        sys.exit(1 if scanner.vulnerabilities_found > 0 else 0)
    
    except Exception as e:
        if not args.quiet:
            print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

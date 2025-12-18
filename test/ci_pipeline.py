#!/usr/bin/env python3
"""
CI/CD PIPELINE - Integración en workflows de Git
Pre-commit y CI validation usando modelo V2
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent


def run_workflow_scanner(target, output_file):
    """Ejecuta workflow scanner"""
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / 'test' / 'workflow_scanner.py'),
        str(target),
        '-r',
        '-o', str(output_file),
        '-q'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def generate_ci_report(results_file):
    """Genera reporte CI"""
    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        vulnerable = sum(1 for r in data['results'] if r.get('vulnerable'))
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'FAILED' if vulnerable > 0 else 'PASSED',
            'total_files_scanned': data['scanned_files'],
            'vulnerable_files': vulnerable,
            'total_vulnerabilities': data['vulnerabilities_found'],
            'details': data['results']
        }
        
        return report
    
    except Exception as e:
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'ERROR',
            'error': str(e)
        }


def main():
    """Pipeline CI/CD"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CI/CD Pipeline')
    parser.add_argument('--stage', choices=['pre-commit', 'ci', 'build'], required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--output', default='ci_report.json')
    
    args = parser.parse_args()
    
    print(f"Ejecutando {args.stage}...")
    
    # Escanea código
    returncode, stdout, stderr = run_workflow_scanner(args.target, args.output)
    
    # Genera reporte
    report = generate_ci_report(args.output)
    
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Status: {report['status']}")
    print(f"Archivos escaneados: {report['total_files_scanned']}")
    print(f"Vulnerabilidades encontradas: {report['total_vulnerabilities']}")
    
    sys.exit(1 if report['status'] == 'FAILED' else 0)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
PRUEBAS EXHAUSTIVAS - MUESTRAS VULNERABLES REALES
Test exhaustivo contra archivos con vulnerabilidades reales
"""

import sys
import os
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime

# Agregar path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modelo_1_detector.model_vulnerabilities import VulnerabilityModel


def extract_functions_python(filepath):
    """Extrae funciones de archivo Python"""
    functions = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    current_func = []
    in_function = False
    indent_level = 0
    
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        
        if stripped.startswith('def '):
            if current_func and in_function:
                functions.append({
                    'name': current_func[0].strip().replace('def ', '').split('(')[0],
                    'lines': current_func,
                    'start_line': i - len(current_func) + 1,
                    'end_line': i
                })
            
            current_func = [line]
            in_function = True
            indent_level = len(line) - len(stripped)
        
        elif in_function:
            current_indent = len(line) - len(stripped) if stripped else 999
            
            if stripped and current_indent <= indent_level:
                functions.append({
                    'name': current_func[0].strip().replace('def ', '').split('(')[0],
                    'lines': current_func,
                    'start_line': i - len(current_func) + 1,
                    'end_line': i - 1
                })
                in_function = False
                current_func = []
            else:
                current_func.append(line)
    
    if current_func:
        functions.append({
            'name': current_func[0].strip().replace('def ', '').split('(')[0],
            'lines': current_func,
            'start_line': len(lines) - len(current_func),
            'end_line': len(lines)
        })
    
    return functions


def extract_functions_js(filepath):
    """Extrae funciones de archivo JavaScript"""
    functions = []
    with open(filepath, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if 'function ' in line or 'const ' in line and '=' in line and '(' in line:
            # Extraer nombre
            if 'function ' in line:
                name = line.split('function ')[1].split('(')[0].strip()
            else:
                name = line.split('const ')[1].split('=')[0].strip()
            
            # Recopilar líneas de la función (aprox)
            func_lines = [line]
            brace_count = line.count('{') - line.count('}')
            
            j = i + 1
            while j < len(lines) and brace_count > 0:
                func_lines.append(lines[j])
                brace_count += lines[j].count('{') - lines[j].count('}')
                j += 1
            
            if name and not name.startswith('//'):
                functions.append({
                    'name': name,
                    'lines': func_lines,
                    'start_line': i + 1,
                    'end_line': j
                })
    
    return functions


def run_comprehensive_test():
    """Ejecuta pruebas exhaustivas"""
    
    print("\n" + "="*90)
    print("PRUEBAS EXHAUSTIVAS - MUESTRAS VULNERABLES REALES")
    print("="*90)
    
    # Crear modelo
    print("\n[1] Inicializando modelo...")
    model = VulnerabilityModel()
    
    # Rutas de prueba
    test_dir = Path(__file__).parent
    python_samples = test_dir / 'vulnerable_samples_python.py'
    js_samples = test_dir / 'vulnerable_samples_js.js'
    
    results = {
        'python': {'vulnerable': [], 'safe': []},
        'javascript': {'vulnerable': [], 'safe': []},
        'summary': {}
    }
    
    # ========================================================================
    # PRUEBAS PYTHON
    # ========================================================================
    if python_samples.exists():
        print(f"\n[2] Analizando Python: {python_samples.name}")
        print("-" * 90)
        
        with open(python_samples, 'r') as f:
            python_content = f.read()
        
        functions = extract_functions_python(str(python_samples))
        
        python_results = model.analyze_code(python_content, language='python')
        
        vulnerable_count = 0
        safe_count = 0
        
        for func in functions:
            func_code = ''.join(func['lines'])
            
            # Detectar si debe ser vulnerable
            func_name = func['name'].lower()
            is_vulnerable = 'vulnerable' in func_name
            
            # Analizar función
            func_results = model.analyze_code(func_code, language='python')
            detected_vulnerable = func_results.get('vulnerable', False)
            
            status = "✓ VULNERABLE" if detected_vulnerable else "✓ SEGURA"
            correct = (detected_vulnerable == is_vulnerable)
            marker = "✓✓" if correct else "✗✗"
            
            if correct:
                if is_vulnerable:
                    vulnerable_count += 1
                    results['python']['vulnerable'].append(func['name'])
                else:
                    safe_count += 1
                    results['python']['safe'].append(func['name'])
            
            if detected_vulnerable:
                vuln_types = ', '.join(func_results.get('summary', {}).get('vulnerability_types', []))
                print(f"{marker} {func['name']:40} [{status:15}] {vuln_types}")
            else:
                print(f"{marker} {func['name']:40} [{status:15}]")
        
        print(f"\nDetección Python: {vulnerable_count} vulnerables, {safe_count} seguras")
    
    # ========================================================================
    # PRUEBAS JAVASCRIPT
    # ========================================================================
    if js_samples.exists():
        print(f"\n[3] Analizando JavaScript: {js_samples.name}")
        print("-" * 90)
        
        with open(js_samples, 'r') as f:
            js_content = f.read()
        
        js_results = model.analyze_code(js_content, language='javascript')
        
        functions = extract_functions_js(str(js_samples))
        
        vulnerable_count = 0
        safe_count = 0
        
        for func in functions:
            func_code = '\n'.join(func['lines'])
            func_name = func['name'].lower()
            is_vulnerable = 'vulnerable' in func_name
            
            func_results = model.analyze_code(func_code, language='javascript')
            detected_vulnerable = func_results.get('vulnerable', False)
            
            status = "✓ VULNERABLE" if detected_vulnerable else "✓ SEGURA"
            correct = (detected_vulnerable == is_vulnerable)
            marker = "✓✓" if correct else "✗✗"
            
            if correct:
                if is_vulnerable:
                    vulnerable_count += 1
                    results['javascript']['vulnerable'].append(func['name'])
                else:
                    safe_count += 1
                    results['javascript']['safe'].append(func['name'])
            
            if detected_vulnerable:
                vuln_types = ', '.join(func_results.get('summary', {}).get('vulnerability_types', []))
                print(f"{marker} {func['name']:40} [{status:15}] {vuln_types}")
            else:
                print(f"{marker} {func['name']:40} [{status:15}]")
        
        print(f"\nDetección JavaScript: {vulnerable_count} vulnerables, {safe_count} seguras")
    
    # ========================================================================
    # RESUMEN
    # ========================================================================
    print("\n" + "="*90)
    print("RESUMEN DE PRUEBAS EXHAUSTIVAS")
    print("="*90)
    
    total_vulns_detected = len(results['python']['vulnerable']) + len(results['javascript']['vulnerable'])
    total_safe_detected = len(results['python']['safe']) + len(results['javascript']['safe'])
    
    print(f"\n✓ Vulnerabilidades detectadas (Python): {len(results['python']['vulnerable'])}")
    print(f"  {', '.join(results['python']['vulnerable'][:5])}...")
    
    print(f"\n✓ Vulnerabilidades detectadas (JavaScript): {len(results['javascript']['vulnerable'])}")
    print(f"  {', '.join(results['javascript']['vulnerable'][:5])}...")
    
    print(f"\n✓ Códigos seguros identificados (Python): {len(results['python']['safe'])}")
    print(f"✓ Códigos seguros identificados (JavaScript): {len(results['javascript']['safe'])}")
    
    print(f"\n{'='*90}")
    print(f"TOTAL: {total_vulns_detected} vulnerabilidades + {total_safe_detected} códigos seguros")
    print(f"{'='*90}")
    
    # Guardar resultados
    results_file = test_dir / 'comprehensive_test_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'python_vulnerable': len(results['python']['vulnerable']),
            'python_safe': len(results['python']['safe']),
            'javascript_vulnerable': len(results['javascript']['vulnerable']),
            'javascript_safe': len(results['javascript']['safe']),
            'total_detected': total_vulns_detected + total_safe_detected,
        }, f, indent=2)
    
    print(f"\n✓ Resultados guardados: {results_file}")
    
    return results


if __name__ == '__main__':
    run_comprehensive_test()

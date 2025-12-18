#!/usr/bin/env python3
"""
TEST SUITE - MODELO PROFESIONAL model_vulnerabilities
Valida precisión, recall, falsos positivos
"""

import json
import time
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'modelo_1_detector'))

from model_vulnerabilities import VulnerabilityModel

print("\n" + "="*90)
print("TEST SUITE - MODELO VULNERABILITIES")
print("="*90)

print("\nCreando modelo...")
model = VulnerabilityModel()
print("✓ Modelo creado\n")

# Test cases
tests = [
    ('[TP] SQL Injection', 'python', 'query = "SELECT * FROM users WHERE id = \'" + user_id + "\'"', True),
    ('[TP] SQL F-String', 'python', 'sql = f"SELECT * FROM {table}"', True),
    ('[TN] SQL Prepared', 'python', 'db.execute("SELECT * WHERE id = %s", [uid])', False),
    ('[TP] XSS innerHTML', 'javascript', 'el.innerHTML = user;', True),
    ('[TN] XSS Safe', 'javascript', 'el.textContent = user;', False),
    ('[TP] Command Inj', 'python', 'os.system(f"ping {host}")', True),
    ('[TN] Command Safe', 'python', 'subprocess.run(["ping", host])', False),
    ('[TP] Pickle', 'python', 'data = pickle.loads(request.data)', True),
    ('[TP] Path Traversal', 'python', 'open(request.args["f"]).read()', True),
    ('[TN] Código Seguro', 'python', 'x = "SELECT * FROM users"', False),
]

print("[RESULTADOS]\n")

tp = tn = fp = fn = 0
times = []

for name, lang, code, expected in tests:
    start = time.time()
    result = model.analyze_code(code, lang)
    elapsed = time.time() - start
    times.append(elapsed)
    
    is_vuln = result['vulnerable']
    
    if is_vuln == expected:
        if is_vuln:
            tp += 1
            outcome = "✓ TP"
        else:
            tn += 1
            outcome = "✓ TN"
        symbol = "✓"
    else:
        if is_vuln:
            fp += 1
            outcome = "✗ FP"
        else:
            fn += 1
            outcome = "✗ FN"
        symbol = "✗"
    
    vuln_str = ""
    if result['vulnerabilities']:
        types = [v['type'] for v in result['vulnerabilities']]
        score = max([v['risk_score'] for v in result['vulnerabilities']], default=0)
        vuln_str = f" [{types[0]} | {score:.2f}]"
    
    print(f"{symbol} {outcome:7} | {name:20} {vuln_str:25} ({elapsed*1000:.0f}ms)")

total = len(tests)
correct = tp + tn
acc = (correct / total * 100) if total > 0 else 0
prec = (tp / (tp + fp) * 100) if (tp + fp) > 0 else 0
fp_rate = (fp / (fp + tn) * 100) if (fp + tn) > 0 else 0

print("\n" + "="*90)
print(f"Accuracy: {acc:.1f}% | Precision: {prec:.1f}% | False Pos Rate: {fp_rate:.1f}%")
print(f"TP: {tp} | TN: {tn} | FP: {fp} | FN: {fn}")
print("="*90)

if acc >= 80 and fp_rate < 15:
    print("✓✓✓ MODELO PRODUCTIVO")
else:
    print(f"⚠ Revisar resultados")
print("="*90 + "\n")

results = {'accuracy': acc, 'precision': prec, 'fp_rate': fp_rate, 'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn}
with open(PROJECT_ROOT / 'test' / 'model_validation_results.json', 'w') as f:
    json.dump(results, f, indent=2)

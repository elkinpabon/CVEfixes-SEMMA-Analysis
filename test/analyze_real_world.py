#!/usr/bin/env python3
"""
ANÁLISIS EXHAUSTIVO - 10 ARCHIVOS REALES COMPLEJOS
Prueba el modelo contra código real con vulnerabilidades no evidentes
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime
import time

# Agregar path del proyecto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modelo_1_detector.model_vulnerabilities import VulnerabilityModel


def analyze_real_world_samples():
    """Analiza los 25 archivos reales"""
    
    print("\n" + "="*100)
    print("ANÁLISIS EXHAUSTIVO - 25 ARCHIVOS REALES COMPLEJOS CON VULNERABILIDADES NO EVIDENTES")
    print("="*100)
    
    # Crear modelo
    print("\n[1] Inicializando modelo...")
    model = VulnerabilityModel()
    print("    ✓ Modelo listo\n")
    
    samples_dir = Path(__file__).parent / 'real_world_samples'
    
    # Lista de archivos y lenguajes esperados
    samples = [
        ('1_flask_app.py', 'python', 'Flask: SQL Injection indirecta'),
        ('2_django_api.py', 'python', 'Django: Command Injection via método'),
        ('3_data_processor.py', 'python', 'Pickle Deserialization + Eval'),
        ('4_file_upload.py', 'python', 'Path Traversal con sanitización incompleta'),
        ('5_template_xss.py', 'python', 'XSS via Template Rendering'),
        ('6_express_api.js', 'javascript', 'Express: SQL + Command Injection'),
        ('7_react_component.jsx', 'javascript', 'React: dangerouslySetInnerHTML + eval'),
        ('8_fastapi_app.py', 'python', 'FastAPI: Async vulnerabilities'),
        ('9_telegram_bot.py', 'python', 'Telegram Bot: SQL + Command Injection'),
        ('10_vue_node.js', 'javascript', 'Vue + Node: CSRF + Prototype Pollution'),
        ('11_secure_fastapi.py', 'python', 'FastAPI: SQLAlchemy mixto (seguro/inseguro)'),
        ('12_mongodb_app.py', 'python', 'MongoDB: NoSQL Injection + eval'),
        ('13_request_app.py', 'python', 'Requests: SSRF + Open Redirect'),
        ('14_mixed_db.py', 'python', 'Mixed Database: Prepared vs f-strings'),
        ('15_crypto_safe.py', 'python', 'Crypto: Safe file operations'),
        ('16_graphql_nosql.py', 'python', 'GraphQL: NoSQL Injection'),
        ('17_grpc_service.py', 'python', 'gRPC: SQL + Command + Pickle'),
        ('18_websocket_server.py', 'python', 'WebSocket: eval + exec + system'),
        ('19_redis_cache.py', 'python', 'Redis: Cache poisoning + command injection'),
        ('20_email_template.py', 'python', 'Email: Template injection'),
        ('21_message_queue.py', 'python', 'RabbitMQ: Pickle + eval + SQL'),
        ('22_oauth_flow.py', 'python', 'OAuth: Open redirect'),
        ('23_file_processor.py', 'python', 'File handling: Path traversal'),
        ('24_search_service.py', 'python', 'ElasticSearch: Query injection'),
        ('25_legacy_code.py', 'python', 'Legacy: Multiple vulnerabilities'),
        ('26_async_api.py', 'python', 'Async API: Background tasks + SQL injection'),
        ('27_microservice_auth.py', 'python', 'Microservice: Auth + SQL injection'),
        ('28_batch_processor.py', 'python', 'Batch: Data processing + exec'),
        ('29_api_gateway.py', 'python', 'API Gateway: Routing + command injection'),
        ('30_streaming_service.py', 'python', 'Streaming: Socket + pickle deserialization'),
        ('31_ai_pipeline.py', 'python', 'AI/ML: Model inference + exec'),
        ('32_payment_processor.py', 'python', 'Payment: Stripe/PayPal + SQL injection'),
        ('33_log_aggregator.py', 'python', 'Logging: ElasticSearch + exec'),
        ('34_cache_layer.py', 'python', 'Cache: Redis/Memcache + command exec'),
        ('35_data_pipeline.py', 'python', 'Data Pipeline: Apache Beam + SQL'),
        ('36_auth_service.py', 'python', 'Sistema de autenticación empresarial'),
        ('37_security_monitor.py', 'python', 'Monitor de seguridad en tiempo real'),
        ('38_billing_system.py', 'python', 'Sistema de facturación empresarial'),
        ('39_search_engine.py', 'python', 'Motor de búsqueda distribuido'),
        ('40_notification_service.py', 'python', 'Sistema de notificaciones'),
        ('41_custom_orm.py', 'python', 'ORM personalizado'),
        ('42_api_proxy.py', 'python', 'Proxy de API gateway'),
        ('43_permissions_engine.py', 'python', 'Sistema de permisos y autorización'),
        ('44_task_orchestrator.py', 'python', 'Orquestador de tareas distribuidas'),
        ('45_sdk_client.py', 'python', 'Cliente SDK para servicios'),
    ]
    
    all_results = []
    total_vulnerabilities = 0
    files_analyzed = 0
    
    print("[2] ANALIZANDO 45 ARCHIVOS REALES (LOS 10 MÁS COMPLEJOS NUEVOS)")
    print("-" * 100)
    
    for filename, language, description in samples:
        filepath = samples_dir / filename
        
        if not filepath.exists():
            print(f"✗ {filename:30} - Archivo no encontrado")
            continue
        
        files_analyzed += 1
        
        # Leer archivo
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        # Analizar
        start_time = time.time()
        result = model.analyze_code(code, language=language)
        elapsed = (time.time() - start_time) * 1000
        
        # Procesar resultados
        vuln_count = result['summary']['total_vulnerabilities']
        vuln_types = ', '.join(result['summary']['vulnerability_types']) if result['summary']['vulnerability_types'] else 'NINGUNA'
        is_vulnerable = "✓ VULNERABLE" if result['vulnerable'] else "✓ SEGURA"
        
        total_vulnerabilities += vuln_count
        
        # Mostrar resultado
        print(f"\n{filename:30} | {is_vulnerable:20}")
        print(f"  Descripción: {description}")
        print(f"  Vulnerabilidades: {vuln_count} ({vuln_types})")
        print(f"  Risk Score: {result['max_risk_score']:.2f} | Tiempo: {elapsed:.0f}ms")
        
        # Detalles de cada vulnerabilidad
        if result['vulnerabilities']:
            for vuln in result['vulnerabilities'][:3]:  # Mostrar top 3
                print(f"    - Línea {vuln['line_number']:3}: {vuln['type']:25} (score: {vuln['risk_score']:.2f})")
        
        all_results.append({
            'filename': filename,
            'language': language,
            'description': description,
            'vulnerable': result['vulnerable'],
            'vulnerability_count': vuln_count,
            'vulnerability_types': result['summary']['vulnerability_types'],
            'max_risk_score': result['max_risk_score'],
            'elapsed_ms': elapsed,
        })
    
    # ========================================================================
    # RESUMEN
    # ========================================================================
    print("\n" + "="*100)
    print("RESUMEN FINAL - ANÁLISIS DE 35 ARCHIVOS REALES")
    print("="*100)
    
    vulnerable_files = sum(1 for r in all_results if r['vulnerable'])
    safe_files = files_analyzed - vulnerable_files
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   Archivos analizados: {files_analyzed}")
    print(f"   Archivos vulnerables: {vulnerable_files} ({vulnerable_files*100//files_analyzed}%)")
    print(f"   Archivos seguros: {safe_files} ({safe_files*100//files_analyzed}%)")
    print(f"   Total vulnerabilidades detectadas: {total_vulnerabilities}")
    
    # Por lenguaje
    python_vulns = sum(r['vulnerability_count'] for r in all_results if r['language'] == 'python')
    js_vulns = sum(r['vulnerability_count'] for r in all_results if r['language'] == 'javascript')
    
    print(f"\n📈 POR LENGUAJE:")
    print(f"   Python: {python_vulns} vulnerabilidades")
    print(f"   JavaScript: {js_vulns} vulnerabilidades")
    
    # Por tipo
    all_types = {}
    for r in all_results:
        for vuln_type in r['vulnerability_types']:
            all_types[vuln_type] = all_types.get(vuln_type, 0) + 1
    
    print(f"\n🔍 POR TIPO DE VULNERABILIDAD:")
    for vuln_type in sorted(all_types.keys()):
        print(f"   {vuln_type:35} {all_types[vuln_type]:3} detecciones")
    
    # Velocidad promedio
    avg_time = sum(r['elapsed_ms'] for r in all_results) / len(all_results)
    print(f"\n⚡ RENDIMIENTO:")
    print(f"   Tiempo promedio de análisis: {avg_time:.0f}ms por archivo")
    
    # Guardar resultados
    results_file = Path(__file__).parent / 'real_world_analysis_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'files_analyzed': files_analyzed,
            'total_vulnerabilities': total_vulnerabilities,
            'vulnerable_files': vulnerable_files,
            'safe_files': safe_files,
            'by_type': all_types,
            'results': all_results,
        }, f, indent=2)
    
    print(f"\n✓ Resultados guardados: {results_file}")
    
    print("\n" + "="*100)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*100)
    
    return all_results


if __name__ == '__main__':
    analyze_real_world_samples()

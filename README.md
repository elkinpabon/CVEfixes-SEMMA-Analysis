# CVEfixes-SEMMA-Analysis: Detector de Vulnerabilidades V1

Detector automático de vulnerabilidades en Python y JavaScript.

**📊 Métricas*
- **Accuracy**: 84.4%
- **Precision**: 85.4%
- **Recall**: 82.5%
- **F1-Score**: 83.9%
- **Specificity**: 33.3%

**🔍 Vulnerabilidades Detectadas**
1. SQL Injection
2. Cross-Site Scripting (XSS)  
3. Command Injection
4. Path Traversal
5. Insecure Deserialization

## 📁 Estructura

```
CVEfixes-SEMMA-Analysis/
├── backend/              # API REST Flask
│   ├── app_model.py
│   └── requirements.txt
├── modelo_1_detector/    # Modelo V1
│   └── model_vulnerabilities.py
├── models/               # Modelos entrenados (.pkl)
├── data/processed/       # Datasets
├── test/                 # Suite de pruebas + 45 ejemplos reales
└── CVEFIXES/            # Dataset CVE fixes
```

## 🚀 Instalación

```bash
pip install -r backend/requirements.txt
```

**Dependencias**: torch, transformers, pandas, scikit-learn, flask, numpy

## � Uso

**Programático:**
```python
from modelo_1_detector.model_vulnerabilities import VulnerabilityModel

model = VulnerabilityModel()
result = model.analyze_code('query = "SELECT * FROM users WHERE id = \'" + user_id + "\'"', language='python')
print(f"Vulnerable: {result['vulnerable']}")
print(f"Risk Score: {result['max_risk_score']:.2f}")
```

**API REST:**
```bash
python backend/app_model.py
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "...", "language": "python"}'
```

## 🧪 Pruebas

```bash
python test/comprehensive_test.py      # Suite completa
python test/integration_test.py        # Pruebas integración
python test/report_effectiveness.py    # Reporte de efectividad
```

## 🏗️ Arquitectura

**Componentes Principales:**
- **VulnerabilityFeatureExtractor**: Extrae features (CodeBERT 768D, AST, flujo datos)
- **DataFlowAnalyzer**: Rastrea entrada → operaciones peligrosas
- **VulnerabilityModel**: Ensemble (75% patrones + 25% semántica)

**Dataset de Entrenamiento:**
- 50,000 muestras de CVEfixes
- 5 tipos de vulnerabilidades
- Python + JavaScript

## 📈 Entrenamiento del Modelo

### Dataset Utilizado
```
Fuente Principal: CVEfixes (CVEFIXES/CVEFixes.csv)
├─ Muestras: 50,000 ejemplos de código
├─ Etiquetado: safe/unsafe (binary classification)
├─ Lenguajes: Python + JavaScript
└─ Cobertura: 5 tipos de vulnerabilidades

Datasets Adicionales:
├─ advanced_vulnerabilities_dataset.csv
├─ cybernative_detector_training.csv
└─ securityeval_cwe_training.csv

Ejemplos:
├─ 45 archivos de prueba
├─ Desde Flask/Django hasta gRPC, WebSocket, ML pipelines
└─ Validación en escenarios reales de producción
```

### Arquitectura del Modelo (VulnerabilityModelV2)

**3 Fases de Análisis Integradas:**

#### Fase 1: Data Flow Analysis 
- **Rastreo multi-línea**: Entrada → operaciones peligrosas
- **Detección de fuentes**: request, input, argv, environ, sockets
- **Identificación de sumideros**: execute, innerHTML, eval, open
- **Validación de sanitización**: Diferencia real vs fake sanitizers
  - Real: parameterized queries, escape HTML, shlex.quote
  - Fake: strip(), replace(), lower(), encode()

#### Fase 2: Type Inference 
- **Inferencia de tipos de variables**: USER_INPUT, STRING_LITERAL, SANITIZED, etc.
- **Reducción de falsos positivos**: Identifica literales de string
- **Análisis AST**: Parse de sintaxis para Python

#### Fase 3: False Positive Filter
- **Contexto seguro**: Detecta test, mock, debug, logs
- **Análisis de comentarios**: Ignora código comentado
- **Clasificación contextual**: Reduce score en entornos seguros

### Características Extraídas (Feature Engineering)

**CodeBERT Embeddings:**
- Modelo pre-entrenado: microsoft/codebert-base
- Dimensión: 768-D vectors
- Captura: Semántica profunda del código
- GPU Support: CUDA si disponible, CPU fallback

**Pattern-Based Features:**
```python
{
  'length': Longitud de línea,
  'complexity': Operadores encontrados,
  'has_concatenation': +, . para strings,
  'has_f_string': f-strings detectados,
  'has_template': Template literals,
  'dangerous_functions': Call patterns,
  'ast_features': Import, assignment, string operations
}
```

**Data Flow Features:**
- has_source: Entrada de usuario detectada
- has_protection: Sanitización presente
- protections: Lista de técnicas usadas
- source_type: Categoría de entrada

### Scoring Ensemble (Ponderado)

```
Score Final = 0.75 × Pattern_Score + 0.25 × Semantic_Score

Pattern Score (línea por línea):
├─ SQL Injection: 0.88 si SQL ops + concat sin protección
├─ XSS: 0.82 si innerHTML sin protección
├─ Command Injection: 0.86 si exec + concat
├─ Path Traversal: 0.79 si file ops + user input
└─ Deserialization: 0.82 si deserialize + user input

Semantic Score:
├─ Cosine similarity: embedding vs vulnerability embeddings
├─ Distancia safe embedding: Comparación con código seguro
└─ Rango: 0.0 - 1.0

Ajustes Dinámicos:
├─ ×1.15 si tiene entrada sin protección
├─ ×0.4 si tiene protecciones detectadas
└─ Threshold: 0.57 para clasificación
```

### Entrenamiento

**Ejecución:**
```bash
python modelo_1_detector/model_vulnerabilities.py
```

**Proceso:**
1. Carga CVEfixes (50,000 muestras)
2. Inicializa CodeBERT y StandardScaler
3. Genera embeddings por tipo de vulnerabilidad
4. Calcula safe_embedding de ejemplos seguros
5. Entrena IsolationForest para anomalías
6. Serializa a pickle (~15MB)

**Tiempo Entrenamiento:** ~2-3 minutos en GPU

### Métricas por Tipo de Vulnerabilidad

| Tipo | Coverage | Precision | Recall | F1 |
|------|----------|-----------|--------|-----|
| SQL Injection | 95.6% | 78% | 96% | 86% |
| Command Injection | 88.6% | 82% | 89% | 85% |
| XSS | 70% | 85% | 70% | 77% |
| Insecure Deserialization | 88.6% | 84% | 89% | 86% |
| Path Traversal | 50% | 50% | 50% | 50% |

### Dependencias Técnicas

```python
# ML & Deep Learning
torch>=1.9.0              # PyTorch
transformers>=4.10.0      # Hugging Face (CodeBERT)
scikit-learn>=0.24.0      # Preprocessing, IsolationForest

# Data Processing
pandas>=1.2.0             # DataFrames
numpy>=1.19.0             # Numerical operations

# Web & API
flask>=2.0.0              # REST API
flask-cors>=3.0.0         # CORS support
```



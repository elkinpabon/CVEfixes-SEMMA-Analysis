# Google Colab Notebooks - Modelos SEMMA

Este directorio contiene dos notebooks de **Google Colab** (Jupyter) optimizados para entrenar los modelos de detección de vulnerabilidades utilizando la metodología **SEMMA**.

## 📓 Notebooks disponibles

### 1. **Modelo_1_Vulnerability_Detector.ipynb**
Detector binario de vulnerabilidades (Vulnerable/Seguro)

**Contenido**:
- ✅ **SETUP**: Instalación de librerías y configuración de Colab
- ✅ **FASE 1 - SAMPLE**: Cargar 9,312 muestras (CyberNative DPO)
- ✅ **FASE 2 - EXPLORE**: Análisis estadístico y distribuciones
- ✅ **FASE 3 - MODIFY**: Feature engineering (TF-IDF 1000 bigramas + lenguaje)
- ✅ **FASE 4 - MODEL**: Entrenar RandomForest (200 árboles)
- ✅ **FASE 5 - ASSESS**: Evaluar métricas, K-Fold CV (5-fold), confusión matrix
- ✅ **INFERENCIA**: Ejemplos de predicción en código nuevo

**Performance esperado**:
- Test Accuracy: **79.01%**
- Recall: **90.12%** (importante: detecta vulnerabilidades)
- 5-Fold CV: **79.22% ± 0.26%**
- ROC-AUC: **88.83%**

**Tiempo de ejecución**: ~1-2 minutos en Colab CPU, ~30 segundos con GPU

---

### 2. **Modelo_2_CWE_Classifier.ipynb**
Clasificador multiclase de tipos de vulnerabilidad (10 tipos CWE)

**Contenido**:
- ✅ **SETUP**: Instalación de librerías y configuración de Colab
- ✅ **FASE 1 - SAMPLE**: Cargar 4,656 muestras vulnerables (SecurityEval)
- ✅ **FASE 2 - EXPLORE**: Consolidar 937 tipos CWE a 10 categorías principales
- ✅ **FASE 3 - MODIFY**: Feature engineering (TF-IDF 1200 trigramas + lenguaje)
- ✅ **FASE 4 - MODEL**: Entrenar RandomForest (250 árboles) + class balancing
- ✅ **FASE 5 - ASSESS**: Evaluar métricas, K-Fold CV (5-fold), por-clase accuracy
- ✅ **INFERENCIA**: Ejemplos de predicción de tipo CWE

**Performance esperado**:
- Test Accuracy: **86.94%**
- Precision: **87.83%**
- 5-Fold CV: **87.62% ± 0.60%**
- Overfitting: **5.28%** (bajo)

**Tiempo de ejecución**: ~3-5 minutos en Colab CPU, ~1-2 minutos con GPU

**Tipos CWE clasificados**:
1. Buffer Overflow (36.4%)
2. SQL Injection (17.1%)
3. Code Injection (15.7%)
4. XSS (5.9%)
5. Null Pointer (9.8%)
6. Insecure Deserialization (4.9%)
7. Memory Management (4.4%)
8. Improper Input Validation (4.0%)
9. Format String Attack (0.9%)
10. Uninitialized Variables (1.0%)

---

## 🚀 Como usar en Google Colab

### Opción 1: Abrir directamente desde GitHub

```
1. Ve a: https://colab.research.google.com/
2. Click en "Archivo" → "Abrir desde GitHub"
3. Pega: elkinpabon/CVEfixes-SEMMA-Analysis
4. Selecciona: colab/Modelo_1_Vulnerability_Detector.ipynb
5. Click abrir
```

### Opción 2: Cargar datos desde tu computadora

En la celda de SETUP:

```python
# Ejecuta esto para subir archivos
from google.colab import files
files.upload()

# Luego usa como dataset_path:
dataset_path = 'cybernative_detector_training.csv'
```

### Opción 3: Usar Google Drive (recomendado)

```python
# En la celda de SETUP:
from google.colab import drive
drive.mount('/content/drive')

# Luego usa como dataset_path:
dataset_path = '/content/drive/MyDrive/CVEfixes/cybernative_detector_training.csv'
```

---

## 📊 Estructura de celdas

Cada notebook está dividido en secciones claras:

```
┌─────────────────────────────────┐
│ SETUP INICIAL (2 celdas)        │
│ - Instalar librerías            │
│ - Importar dependencias         │
│ - Configurar Colab              │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│ FASE 1: SAMPLE (2-3 celdas)     │
│ - Cargar CSV                    │
│ - Validar estructura            │
│ - Ver distribución              │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│ FASE 2: EXPLORE (3-4 celdas)    │
│ - Análisis estadístico          │
│ - Visualizaciones               │
│ - Características               │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│ FASE 3: MODIFY (4-5 celdas)     │
│ - TF-IDF vectorización          │
│ - Feature encoding              │
│ - Train/Test split              │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│ FASE 4: MODEL (1-2 celdas)      │
│ - Configurar RandomForest       │
│ - Entrenar modelo               │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│ FASE 5: ASSESS (5-7 celdas)     │
│ - Predicciones                  │
│ - Metricas                      │
│ - K-Fold validation             │
│ - Visualizaciones               │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│ INFERENCIA (1-2 celdas)         │
│ - Ejemplos de uso               │
│ - Predicciones nuevas           │
└─────────────────────────────────┘
```

---

## 📥 Cargar datasets en Colab

### CSV files necesarios:

```
cybernative_detector_training.csv
├─ Size: ~5 MB
├─ Rows: 9,312
├─ Columns: codigo, lenguaje, vulnerable
└─ Source: CyberNative DPO (Hugging Face)

securityeval_cwe_training.csv (Modelo 2 solo)
├─ Size: ~4 MB
├─ Rows: 4,656
├─ Columns: codigo, lenguaje, tipo_vulnerabilidad
└─ Source: SecurityEval Dataset
```

**Los notebooks usarán el primer CSV, que contiene ambos tipos de datos.**

---

## 🎯 Tips para Colab

### Performance optimization

```python
# Usar GPU (si disponible)
# En Colab: Runtime → Change runtime type → GPU

# Aumentar RAM disponible
# En Colab: Tools → Settings → High RAM

# Desactivar salida verbose
warnings.filterwarnings('ignore')
```

### Guardar modelos en Google Drive

```python
# Montar Drive
from google.colab import drive
drive.mount('/content/drive')

# Guardar modelo
pickle.dump(model, open('/content/drive/MyDrive/model.pkl', 'wb'))
```

### Descargar resultados

```python
# Descargar archivo local
from google.colab import files
files.download('mi_archivo.pkl')
```

---

## 📊 Características de los notebooks

### Visualizaciones incluidas

✅ **Modelo 1**:
- Distribución de clases
- Longitud de código
- Distribución de lenguajes
- Box plot por clase
- Matriz de confusión
- Curva ROC
- K-Fold scores

✅ **Modelo 2**:
- Distribución CWE consolidada
- Lenguajes en datos vulnerables
- Matriz de confusión
- Metricas de performance
- K-Fold scores
- Accuracy por clase

### Validaciones automáticas

✅ Verificar columnas requeridas
✅ Detectar valores nulos
✅ Detectar duplicados
✅ Validar balanceo de clases
✅ Verificar proporciones train/test
✅ Evaluar overfitting

---

## ⚙️ Personalización

Puedes ajustar hiperparámetros fácilmente:

```python
# RandomForest
n_estimators=200  # Aumentar para mejor accuracy (mas lento)
max_depth=25      # Reducir para evitar overfitting
min_samples_split=5  # Aumentar para modelo mas simple

# TF-IDF
max_features=1000    # Aumentar para mas features
ngram_range=(1, 2)   # Cambiar a (1, 3) para trigramas
min_df=2             # Aumentar para ignorar palabras raras
max_df=0.95          # Reducir para ignorar palabras muy frecuentes

# K-Fold
n_splits=5      # Cambiar numero de folds
```

---

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| **ModuleNotFoundError** | Ejecutar celda de SETUP |
| **FileNotFoundError** | Verificar ruta dataset_path |
| **Memory error** | Activar GPU en Colab |
| **Stratify error** | Usar notebook Modelo 2 (filtra automaticamente) |
| **No data in test set** | Verificar balanceo de clases |

---

## 📝 Archivos relacionados

```
../
├── modelo_1_detector/
│   └── vulnerability_detector.py  (version local)
├── modelo_2_clasificador/
│   └── cwe_classifier.py         (version local)
├── data/processed/
│   ├── cybernative_detector_training.csv
│   └── securityeval_cwe_training.csv
└── README.md (documentacion general)
```

---

## 📖 Referencias SEMMA

- **S**ample: Seleccionar datos relevantes
- **E**xplore: Entender distribuciones y relaciones
- **M**odify: Transformar datos para modelado
- **M**odel: Entrenar y ajustar algoritmos
- **A**ssess: Evaluar performance y generalización

Este es el framework estándar de SAS Institute para proyectos de data mining.

---

## ✅ Checklist de uso

- [ ] Abrir notebook en Colab
- [ ] Ejecutar SETUP (instalar librerías)
- [ ] Cargar dataset (upload o Google Drive)
- [ ] Ejecutar FASE 1-5 en orden
- [ ] Revisar visualizaciones
- [ ] Guardar modelos (opcional)
- [ ] Probar INFERENCIA con código nuevo
- [ ] Descargar resultados

---

**Última actualización**: 3 de diciembre de 2025  
**Estado**: ✅ Listos para usar en Google Colab  
**Repositorio**: elkinpabon/CVEfixes-SEMMA-Analysis

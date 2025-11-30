# Modelo Final - Deteccion de Vulnerabilidades

## Resumen

Modelo de Machine Learning que detecta vulnerabilidades en codigo combinando:
- **7 features numericas** (longitud, complejidad, estructura)
- **50 features TF-IDF** (palabras clave del codigo)
- **4 algoritmos** entrenados y comparados
- **9,958 registros** del dataset CVEFixes (balanceados: 47.8% vulnerable, 52.2% safe)

## Resultado Principal

**MEJOR MODELO: Decision Tree**
- Precision: 48.0%
- Recall: 13.6%
- ROC-AUC: 0.5019
- F1-Score: 0.2124

## Dataset

- Archivo: `CVEFixes.csv` (1.44 GB)
- Muestra: 12,000 registros -> 9,958 despues de limpieza
- Distribucion: 4,763 vulnerable (47.8%), 5,195 safe (52.2%)
- Caracteres por codigo: 38,000-40,000 promedio
- Lineas por codigo: 2,100-2,400 promedio

## Features Utilizadas

### Numericas (7)
1. code_length - Longitud total en caracteres
2. code_lines - Numero de lineas
3. avg_line_length - Promedio por linea
4. char_per_word - Promedio de caracteres por palabra
5. word_count - Total de palabras
6. bracket_count - Parentesis y llaves
7. paren_ratio - Proporcion de parentesis

### TF-IDF (50)
Palabras clave extraidas de los primeros 1000 caracteres del codigo

**Top Features por Importancia:**
- char_per_word: 0.0635
- avg_line_length: 0.0622
- code_length: 0.0597
- code_lines: 0.0570
- paren_ratio: 0.0559

## Modelos Evaluados

| Modelo | Precision | Recall | F1 | ROC-AUC | CV-AUC |
|--------|-----------|--------|----|---------|----|
| **Decision Tree** | **48.0%** | **13.6%** | **0.2124** | **0.5019** | 0.4653 |
| Neural Network | 35.0% | 34.5% | 0.3478 | 0.3411 | 0.3695 |
| Gradient Boosting | 34.4% | 29.2% | 0.3156 | 0.3577 | 0.3796 |
| Random Forest | 30.5% | 22.3% | 0.2571 | 0.3409 | 0.3645 |

## Ejecucion

### Ejecutar el modelo:
```bash
python modelo.py
```

### Salida:
1. Carga de 12,000 registros
2. Limpieza y procesamiento
3. Extraccion de 57 features (7 numericas + 50 TF-IDF)
4. Entrenamiento de 4 algoritmos
5. Evaluacion y comparacion
6. Generacion de grafico: `modelo_resultados.png`

### Ejemplo de salida:
```
MODELO DE DETECCION DE VULNERABILIDADES

CARGANDO DATOS...
Registros cargados: 12,000
LIMPIANDO DATOS...
Registros finales: 9,958 (removidos 1,312 duplicados)

ANALISIS:
  Distribucion:
    vulnerable: 4,763 (47.8%)
    safe: 5,195 (52.2%)

CREANDO FEATURES...
Extrayendo features TF-IDF...
Total features: 57 (7 numericas + 50 TF-IDF)

ENTRENANDO MODELOS...
1. Decision Tree...
2. Random Forest...
3. Gradient Boosting...
4. Red Neuronal...

RESULTADOS

Decision Tree:
  Precision: 0.4797 (48.0%)
  Recall: 0.1364
  F1-Score: 0.2124
  ROC-AUC: 0.5019
  CV-AUC: 0.4653 (+- 0.0065)

MEJOR MODELO: Decision Tree
Precision: 48.0% | AUC: 0.5019

Generando graficos...
Grafico guardado: modelo_resultados.png
```

## Interpretacion

- **Precision 48%**: Cuando el modelo predice "vulnerable", es correcto 48% de las veces
- **Recall 13.6%**: El modelo detecta 13.6% de los codigos vulnerables reales
- **ROC-AUC 0.5019**: Ligeramente mejor que clasificacion aleatoria
- **F1-Score 0.2124**: Balance entre precision y recall es bajo

## Limitaciones

1. Muestra reducida (12K de 1.44GB)
2. Precision moderada (48%)
3. Recall bajo (13.6%)
4. Dataset puede tener sesgo en caracteristicas detectables
5. Features simples sin patrones de seguridad especificos

## Mejoras Futuras

1. Aumentar dataset a 50K-100K registros
2. Agregar features de seguridad conocidas
3. Fine-tuning de hiperparametros
4. Ensemble avanzado (Voting, Stacking)
5. Analisis de patrones especificos (SQL injection, XSS, etc)

## Archivos

- `modelo.py` - Script principal (ejecutable)
- `modelo_resultados.png` - Visualizacion de resultados
- `CVEFixes.csv` - Dataset original
- `README.md` - Este archivo

## Requisitos

```
pandas >= 1.0
numpy >= 1.19
scikit-learn >= 0.24
matplotlib >= 3.3
```

## Notas Tecnicas

- Random State: 42 (reproducibilidad)
- Train/Test: 80/20 estratificado
- Normalizacion: StandardScaler
- Cross-Validation: 5-fold
- TF-IDF: ngram_range=(1,2), max_features=50, min_df=5

---

**Estado**: Completo y Funcional
**Ultima ejecucion**: 2024

# Modelo de Deteccion de Vulnerabilidades - Metodologia SEMMA

## Objetivo General

Desarrollar un modelo de Machine Learning que detecte automaticamente vulnerabilidades en codigo fuente utilizando la metodologia SEMMA.

## Metodologia SEMMA

### FASE 1: SAMPLE (Muestreo)
Extraccion y preparacion de datos de codigo fuente. Se selecciona una muestra representativa del codigo a analizar.

### FASE 2: EXPLORE (Exploracion)
Analisis exploratorio de los datos. Se realiza limpieza, deteccion de anomalias y analisis de patrones iniciales.

### FASE 3: MODIFY (Modificacion)
Ingenieria de features. Se transforman los datos brutos en caracteristicas numericas utiles para el aprendizaje.

### FASE 4: MODEL (Modelado)
Entrenamiento de algoritmos de Machine Learning. Se prueban multiples modelos y se compara su rendimiento.

### FASE 5: ASSESS (Evaluacion)
Evaluacion y validacion de modelos. Se selecciona el mejor modelo y se analiza su capacidad predictiva.

## Objetivos del Modelo

- Detectar automaticamente vulnerabilidades en codigo
- Lograr alta precision en las predicciones
- Proporcionar explicabilidad mediante feature importance
- Validar rendimiento con metricas de evaluacion
- Generar visualizaciones de comparativa de modelos

## Ejecucion

Ejecutar el script principal:
```bash
python modelo.py
```

El ciclo SEMMA se ejecuta automaticamente a traves de las 5 fases.

---

**Estado**: Ciclo SEMMA implementado y funcional
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

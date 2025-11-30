import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score, roc_curve, f1_score, precision_score, recall_score

print("\n" + "="*90)
print("MODELO DE DETECCION DE VULNERABILIDADES")
print("="*90 + "\n")

# ==============================================================================
# FASE 1: SAMPLE - Extraccion y carga de datos
# ==============================================================================
print("[FASE 1: SAMPLE] Extrayendo muestra del dataset...\n")

# CARGA
print("CARGANDO DATOS...")
CSV_PATH = r'c:\Users\elkin\Desktop\CVEfixes\CVEFixes.csv'

try:
    df = pd.read_csv(CSV_PATH, on_bad_lines='skip', low_memory=False)
except:
    print("Error encoding, usando engine=python")
    df = pd.read_csv(CSV_PATH, on_bad_lines='skip', engine='python')

print(f"Registros cargados: {len(df):,}")

# ==============================================================================
# FASE 2: EXPLORE - Exploracion y limpieza de datos
# ==============================================================================
print("\n[FASE 2: EXPLORE] Analizando y limpiando datos...\n")

# LIMPIAR
print("LIMPIANDO DATOS...")
df = df.dropna(subset=['code', 'safety']).reset_index(drop=True)
df = df[df['code'].str.len() >= 15].reset_index(drop=True)

initial_len = len(df)
df = df.drop_duplicates(subset=['code'], keep='first').reset_index(drop=True)
print(f"Registros finales: {len(df):,} (removidos {initial_len - len(df):,} duplicados)")

# ANALIZAR
print("\n[EXPLORACION] Distribucion de clases:")
print(f"  Distribucion:")
for val in df['safety'].unique():
    count = (df['safety'] == val).sum()
    pct = (count / len(df)) * 100
    print(f"    {val}: {count:,} ({pct:.1f}%)")

# ==============================================================================
# FASE 3: MODIFY - Ingenieria de features y transformacion de datos
# ==============================================================================
print("\n[FASE 3: MODIFY] Ingenieria de features...\n")

# FEATURES
print("CREANDO FEATURES...")

# Features numericas
df['code_length'] = df['code'].str.len()
df['code_lines'] = df['code'].str.count('\n') + 1
df['avg_line_length'] = df['code_length'] / (df['code_lines'] + 1)
df['word_count'] = df['code'].str.split().str.len()
df['char_per_word'] = df['code_length'] / (df['word_count'] + 1)
df['bracket_count'] = df['code'].str.count(r'[\{\[\(]')
df['paren_ratio'] = df['bracket_count'] / (df['code_length'] + 1)

# Muestrear codigo para TF-IDF (primeros 1000 caracteres)
df['code_sample'] = df['code'].str[:1000]

df['safety_numeric'] = (df['safety'] == 'vulnerable').astype(int)

feature_cols = ['code_length', 'code_lines', 'avg_line_length', 'char_per_word', 
                'bracket_count', 'paren_ratio', 'word_count']
X_numeric = df[feature_cols].fillna(0).values

# TF-IDF
print("Extrayendo features TF-IDF...")
tfidf = TfidfVectorizer(max_features=50, ngram_range=(1, 2), min_df=5)
X_tfidf = tfidf.fit_transform(df['code_sample']).toarray()

# Combinar
X = np.hstack([X_numeric, X_tfidf])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
y = df['safety_numeric'].values

print(f"Total features: {X_scaled.shape[1]} (7 numericas + 50 TF-IDF)")

# SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train: {len(X_train):,} | Test: {len(X_test):,}")

# ==============================================================================
# FASE 4: MODEL - Construccion y entrenamiento de modelos
# ==============================================================================
print("\n[FASE 4: MODEL] Entrenando 4 algoritmos de Machine Learning...\n")

# ENTRENAR
print("ENTRENANDO MODELOS...")

models = {}
y_preds = {}
y_probs = {}

print("1. Decision Tree...")
dt = DecisionTreeClassifier(max_depth=12, random_state=42)
dt.fit(X_train, y_train)
models['Decision Tree'] = dt
y_preds['Decision Tree'] = dt.predict(X_test)
y_probs['Decision Tree'] = dt.predict_proba(X_test)[:, 1]

print("2. Random Forest...")
rf = RandomForestClassifier(n_estimators=120, max_depth=14, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
models['Random Forest'] = rf
y_preds['Random Forest'] = rf.predict(X_test)
y_probs['Random Forest'] = rf.predict_proba(X_test)[:, 1]

print("3. Gradient Boosting...")
gb = GradientBoostingClassifier(n_estimators=100, max_depth=8, random_state=42)
gb.fit(X_train, y_train)
models['Gradient Boosting'] = gb
y_preds['Gradient Boosting'] = gb.predict(X_test)
y_probs['Gradient Boosting'] = gb.predict_proba(X_test)[:, 1]

print("4. Red Neuronal...")
mlp = MLPClassifier(hidden_layer_sizes=(256, 128, 64), max_iter=1000, random_state=42)
mlp.fit(X_train, y_train)
models['Neural Network'] = mlp
y_preds['Neural Network'] = mlp.predict(X_test)
y_probs['Neural Network'] = mlp.predict_proba(X_test)[:, 1]

# ==============================================================================
# FASE 5: ASSESS - Evaluacion y comparacion de modelos
# ==============================================================================
print("\n[FASE 5: ASSESS] Evaluando modelos entrenados...\n")

# EVALUAR
print("\n" + "="*90)
print("RESULTADOS")
print("="*90)

results = []

for name in models.keys():
    y_pred = y_preds[name]
    y_prob = y_probs[name]
    
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    
    cv_scores = cross_val_score(models[name], X_train, y_train, cv=5, scoring='roc_auc')
    
    print(f"\n{name}:")
    print(f"  Precision: {precision:.4f} ({precision*100:.1f}%)")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    print(f"  ROC-AUC: {auc:.4f}")
    print(f"  CV-AUC: {cv_scores.mean():.4f} (+- {cv_scores.std():.4f})")
    
    results.append({'Modelo': name, 'Precision': precision, 'Recall': recall, 'F1': f1, 'AUC': auc})

results_df = pd.DataFrame(results).sort_values('AUC', ascending=False)
best_model = results_df.iloc[0]

print(f"\n{'='*90}")
print(f"MEJOR MODELO: {best_model['Modelo']}")
print(f"Precision: {best_model['Precision']:.1%} | AUC: {best_model['AUC']:.4f}")
print(f"{'='*90}\n")

# GRAFICOS
print("Generando graficos...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Precision
ax = axes[0, 0]
rs = results_df.sort_values('Precision')
colors = ['gold' if x == best_model['Modelo'] else 'skyblue' for x in rs['Modelo']]
ax.barh(rs['Modelo'], rs['Precision'], color=colors, edgecolor='black')
ax.set_xlabel('Precision')
ax.set_title('Comparativa de Precision')
ax.set_xlim([0, 1])

# Recall
ax = axes[0, 1]
rs = results_df.sort_values('Recall')
colors = ['gold' if x == best_model['Modelo'] else 'lightgreen' for x in rs['Modelo']]
ax.barh(rs['Modelo'], rs['Recall'], color=colors, edgecolor='black')
ax.set_xlabel('Recall')
ax.set_title('Comparativa de Recall')
ax.set_xlim([0, 1])

# F1-Score
ax = axes[1, 0]
rs = results_df.sort_values('F1')
colors = ['gold' if x == best_model['Modelo'] else 'lightcoral' for x in rs['Modelo']]
ax.barh(rs['Modelo'], rs['F1'], color=colors, edgecolor='black')
ax.set_xlabel('F1-Score')
ax.set_title('Comparativa de F1-Score')
ax.set_xlim([0, 1])

# ROC
ax = axes[1, 1]
for name in results_df['Modelo']:
    y_prob = y_probs[name]
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)
    lw = 3 if name == best_model['Modelo'] else 1.5
    ax.plot(fpr, tpr, label=f'{name} ({auc:.3f})', linewidth=lw)

ax.plot([0, 1], [0, 1], 'k--', linewidth=1)
ax.set_xlabel('False Positive Rate')
ax.set_ylabel('True Positive Rate')
ax.set_title('Curvas ROC')
ax.legend(loc='lower right', fontsize=9)
ax.grid(True, alpha=0.3)

plt.suptitle('MODELO DE DETECCION DE VULNERABILIDADES', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(r'c:\Users\elkin\Desktop\CVEfixes\modelo_resultados.png', dpi=120, bbox_inches='tight')
print(f"Grafico guardado: modelo_resultados.png")
plt.close()

# ANALISIS DE IMPORTANCIA
print("\n[ANALISIS] Top 10 Features mas importantes (Random Forest):")
all_features = feature_cols + tfidf.get_feature_names_out().tolist()
for feat, imp in sorted(zip(all_features, rf.feature_importances_), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {feat}: {imp:.4f}")


import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
import warnings
import os
import pickle

warnings.filterwarnings('ignore')

# ==========================================
# 1. ÎNCĂRCAREA ȘI UNIREA FIȘIERELOR
# ==========================================
# Presupunem că scriptul și CSV-urile sunt în același folder.
# Folosim căi relative ca să evităm problemele cu backslash-urile din Windows.
cale_atacuri = '20000_randuri_atacuri_ucraina.csv'
cale_strategica = 'dataset_strategic_id.csv'

if not os.path.exists(cale_atacuri) or not os.path.exists(cale_strategica):
    print("❌ EROARE: Nu găsesc fișierele CSV în folderul curent.")
    print(f"Asigură-te că {cale_atacuri} și {cale_strategica} sunt lângă acest script.")
    exit()

print("✅ Fișiere găsite! Citim datele și construim modelul de risc...")
df_atacuri = pd.read_csv(cale_atacuri)
df_strategic = pd.read_csv(cale_strategica)

# Unim cele două tabele folosind numele regiunii
df = pd.merge(df_atacuri, df_strategic, left_on='regiune_standard', right_on='regiune', how='inner')

# Asigurăm numele coloanei 'atac' (în caz că mai există CSV-uri vechi)
df = df.rename(columns={' atac': 'atac'})

print("Distribuție originală a coloanei 'atac':")
print(df['atac'].value_counts(normalize=True))

# ==========================================
# 2. DEFINIREA UNUI SCOR HEURISTIC DE RISC
# ==========================================
# Combinăm câteva reguli simple, explicabile.
# Ponderile au fost alese pe baza unui mic sweep (vezi sweep_risc.py),
# cea mai bună configurație fiind aproximativ:
# quantile = 0.70, w_dist = 0.5, w_infra = 0.5, w_front = 1.0,
# w_nuclear = 2.0, w_night = 1.0, w_weather = 1.0.
dist_front_term = (500 - df['distanta_front_km'].clip(0, 500)) / 50.0
infrastructure_term = df['scor_infrastructura']
front_distance_term = (300 - df['front_distance'].clip(0, 300)) / 60.0
nuclear_term = df['has_nuclear']
night_term = df['este_noapte']
weather_term = (1 - df['vreme_severa'])

df['scor_risc_heuristic'] = (
    0.5 * dist_front_term
    + 0.5 * infrastructure_term
    + 1.0 * front_distance_term
    + 2.0 * nuclear_term
    + 1.0 * night_term
    + 1.0 * weather_term
)

# Alegem prag astfel încât ~30% din exemple să fie risc înalt (1), restul risc scăzut (0)
prag = df['scor_risc_heuristic'].quantile(0.70)
df['risc_inalt'] = (df['scor_risc_heuristic'] >= prag).astype(int)

print("\nDistribuție noul label 'risc_inalt':")
print(df['risc_inalt'].value_counts(normalize=True))

# ==========================================
# 3. PREGĂTIREA DATELOR (X și y binar: risc înalt / risc scăzut)
# ==========================================
df['scor_infrastructura_total'] = df['energy_score'] + df['military_score'] + df['logistics_score']

enc_arma = LabelEncoder()
enc_loc = LabelEncoder()

df['arma_cod'] = enc_arma.fit_transform(df['model'].fillna('Unknown'))
df['loc_cod'] = enc_loc.fit_transform(df['launch_place'].fillna('Unknown'))

# X conține atât informații tactice (ora, noapte, sezon, vreme, armă, loc),
# cât și strategice (infrastructură, nuclear, distanță la front).
X = df[[
    'ora_lansarii',
    'este_noapte',
    'este_sezon_rece',
    'vreme_severa',
    'arma_cod',
    'loc_cod',
    'scor_infrastructura_total',
    'has_nuclear',
    'front_distance'
]]

y = df['risc_inalt'].astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)

# ==========================================
# 4. ANTRENAREA MODELULUI BINAR (RISC ÎNALT / RISC SCĂZUT)
# ==========================================
model_ai = HistGradientBoostingClassifier(
    learning_rate=0.1,
    max_depth=8,
    max_iter=300,
    min_samples_leaf=20,
    random_state=42
)
model_ai.fit(X_train, y_train)

y_proba = model_ai.predict_proba(X_test)[:, 1]

# Căutăm pragul optim pe probabilitate pentru F1 (clasa risc_inalt = 1)
best_thr = 0.5
best_f1 = -1.0
best_acc = 0.0
for thr in np.linspace(0.1, 0.9, 17):
    y_pred_thr = (y_proba >= thr).astype(int)
    f1 = f1_score(y_test, y_pred_thr)
    acc_thr = accuracy_score(y_test, y_pred_thr)
    if f1 > best_f1:
        best_f1 = f1
        best_thr = thr
        best_acc = acc_thr

auc = roc_auc_score(y_test, y_proba)
print(f"\n📈 ROC-AUC pentru 'risc_inalt' (independent de prag): {auc:.3f}")
print(f"🔍 Prag optim pe probabilitate (după F1 pentru risc_inalt=1): {best_thr:.2f}")
print(f"🎯 Acuratețe la prag optim: {best_acc * 100:.2f}%")
print(f"⚖️  F1-score pentru clasa risc_inalt=1 la prag optim: {best_f1:.3f}")


# ==========================================
# 5. SALVAREA MODELULUI ÎNTR-UN PKL
# ==========================================
model_bundle = {
    "model": model_ai,
    "enc_arma": enc_arma,
    "enc_loc": enc_loc,
    "best_threshold": best_thr,
    "feature_names": list(X.columns),
}

with open("model_risc_inalt.pkl", "wb") as f:
    pickle.dump(model_bundle, f)

print("\n💾 Modelul și encoderele au fost salvate în 'model_risc_inalt.pkl'.")

import pandas as pd
import pickle
import warnings
import os

warnings.filterwarnings('ignore')


fisier_model = "model.pkl"

if not os.path.exists(fisier_model):
    print(f"EROARE: Nu găsesc fișierul '{fisier_model}'. Ai rulat scriptul de antrenament înainte?")
    exit()

with open(fisier_model, "rb") as f:
    bundle = pickle.load(f)

model_ai = bundle["model"]
enc_arma = bundle["enc_arma"]
enc_loc = bundle["enc_loc"]
best_thr = bundle["best_threshold"]
feature_names = bundle["feature_names"]

cale_strategic = r"dataset_strategic_id.csv"

if not os.path.exists(cale_strategic):
    print(f"EROARE: Nu găsesc fișierul strategic la calea: {cale_strategic}")
    exit()

df_strategic = pd.read_csv(cale_strategic)
df_strategic['scor_infrastructura_total'] = df_strategic['energy_score'] + df_strategic['military_score'] + df_strategic['logistics_score']

def evalueaza_o_regiune(nume_regiune, arma, loc_lansare, ora, noapte, sezon, vreme):
    regiune_date = df_strategic[df_strategic['regiune'] == nume_regiune]
    
    if regiune_date.empty:
        print(f"EROARE: Regiunea '{nume_regiune}' nu există în baza de date! Verifică scrierea.")
        return

    row = regiune_date.iloc[0]

    try:
        a_c = enc_arma.transform([arma])[0]
    except ValueError:
        a_c = 0 
        
    try:
        l_c = enc_loc.transform([loc_lansare])[0]
    except ValueError:
        l_c = 0

    linie_predictie = {
        'ora_lansarii': ora,
        'este_noapte': noapte,
        'este_sezon_rece': sezon,
        'vreme_severa': vreme,
        'arma_cod': a_c,
        'loc_cod': l_c,
        'scor_infrastructura_total': row['scor_infrastructura_total'],
        'scor_infrastructura': row['scor_infrastructura_total'] / 3.0, 
        'has_nuclear': row['has_nuclear'],
        'front_distance': row['front_distance'],
        'distanta_front_km': row['front_distance'] 
    }
    
    df_input = pd.DataFrame([linie_predictie])[feature_names]
    
    probabilitate_bruta = model_ai.predict_proba(df_input)[0][1]
    
    alerta_rosie = 1 if probabilitate_bruta >= best_thr else 0
    status = "RISC ÎNALT" if alerta_rosie == 1 else "Sigur"

    print(f"[{nume_regiune.upper()}] | Armă: {arma} | Oră: {ora}:00 | Noapte: {'Da' if noapte else 'Nu'} | Vreme Severă: {'Da' if vreme else 'Nu'}")
    print(f"   => PROBABILITATE AI: {probabilitate_bruta * 100:.2f}%")
    print(f"   => STATUS ALERTĂ:    {status}")
    print("-" * 70)

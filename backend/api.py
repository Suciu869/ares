from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import pickle
import random
import os
import requests
from datetime import datetime

app = FastAPI(title="Radar Intel API - Linked to React")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


fisier_model = "model.pkl"

if not os.path.exists(fisier_model):
    raise FileNotFoundError(f" EROARE: Fișierul '{fisier_model}' nu există!")

with open(fisier_model, "rb") as f:
    bundle = pickle.load(f)

model_ai = bundle["model"]
enc_arma = bundle["enc_arma"]
enc_loc = bundle["enc_loc"]
best_thr = bundle["best_threshold"]
feature_names = bundle["feature_names"]

df_strategic = pd.read_csv("dataset_strategic_id.csv")
df_strategic['scor_infrastructura_total'] = df_strategic['energy_score'] + df_strategic['military_score'] + df_strategic['logistics_score']


DICTIONAR_ISO = {
    "UA05": "Vinnytsia oblast", "UA07": "Volyn oblast", "UA09": "Luhansk oblast", 
    "UA12": "Dnipropetrovsk oblast", "UA14": "Donetsk oblast", "UA18": "Zhytomyr oblast", 
    "UA21": "Zakarpattia oblast", "UA23": "Zaporizhzhia oblast", "UA26": "Ivano-Frankivsk oblast",
    "UA30": "Kyiv (Oblast)", "UA32": "Kyiv (Oraș)", "UA35": "Kirovohrad oblast", 
    "UA40": "Sevastopol (Oraș)", "UA43": "Republica Autonomă Crimeea", "UA46": "Lviv oblast", 
    "UA48": "Mykolaiv oblast", "UA51": "Odesa oblast", "UA53": "Poltava oblast",
    "UA56": "Rivne oblast", "UA59": "Sumy oblast", "UA61": "Ternopil oblast", 
    "UA63": "Kharkiv oblast", "UA65": "Kherson oblast", "UA68": "Khmelnytskyi oblast", 
    "UA71": "Cherkasy oblast", "UA74": "Chernihiv oblast", "UA77": "Chernivtsi oblast"
}

# Funcție pentru vreme (opțională, nu crapă dacă nu pui cheia)
def ia_vremea_reala(regiune: str):
    API_KEY = "5bb9d9f5a8644a4e82e232305261403" # Cheia ta
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={regiune}, Ukraine"
    try:
        raspuns = requests.get(url, timeout=3).json()
        conditie = raspuns['current']['condition']['text'].lower()
        vreme_rea = ['rain', 'snow', 'storm', 'thunder', 'blizzard', 'heavy', 'ice', 'drizzle']
        return 1 if any(cu in conditie for cu in vreme_rea) else 0
    except:
        return 0


class CerereFrontend(BaseModel):
    region_id: str

@app.post("/api/evalueaza-regiune")
def evalueaza_api(date: CerereFrontend):
    # 1. Traducem codul venit de la React în numele corect pentru Pandas
    nume_cautat = DICTIONAR_ISO.get(date.region_id.upper())
    
    if not nume_cautat:
        return {"eroare": f"Codul regiunii {date.region_id} nu a fost recunoscut."}

    # 2. Căutăm regiunea în Excel
    regiune_date = df_strategic[df_strategic['regiune'] == nume_cautat]
    if regiune_date.empty:
        return {"eroare": f"Regiunea '{nume_cautat}' lipsește din Excel!"}
        
    row = regiune_date.iloc[0]

    # 3. Date logice pentru Model
    ora_curenta = datetime.now().hour
    este_noapte_real = 1 if (ora_curenta >= 20 or ora_curenta <= 6) else 0
    sezon_ales = 1 if datetime.now().month in [11, 12, 1, 2, 3] else 0 
    vreme_severa_reala = ia_vremea_reala(nume_cautat)

    lista_arme = ['Shahed-136/131', 'Iskander-M/KN-23', 'Kh-101/Kh-555/Kh-55', 'Kalibr']
    arma_aleasa = random.choice(lista_arme)
    loc_ales = random.choice(['Primorsko-Akhtarsk', 'Kursk oblast', 'Chauda, Crimea', 'Olenya', 'Caspian Sea'])

    try: a_c = enc_arma.transform([arma_aleasa])[0]
    except: a_c = 0 
    try: l_c = enc_loc.transform([loc_ales])[0]
    except: l_c = 0

    linie_predictie = {
        'ora_lansarii': ora_curenta,
        'este_noapte': este_noapte_real,
        'este_sezon_rece': sezon_ales,
        'vreme_severa': vreme_severa_reala,
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
    

    return {
        "energy_score": int(row['energy_score']),
        "military_score": int(row['military_score']),
        "logistics_score": int(row['logistics_score']),
        "has_nuclear": "yes" if int(row['has_nuclear']) == 1 else "no",
        "risk_percent": float(round(probabilitate_bruta * 100, 2))
    }
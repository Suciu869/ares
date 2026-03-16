import itertools

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


def build_risk_label(df, w_dist=1.0, w_infra=1.0, w_front=1.0, w_nuclear=2.0, w_night=2.0, w_weather=1.5, quantile=0.70):
    """Construiește scorul heuristic și eticheta risc_inalt pentru un set dat de ponderi + cuantila."""
    dist_front_term = (500 - df["distanta_front_km"].clip(0, 500)) / 50.0
    infrastructure_term = df["scor_infrastructura"]
    front_distance_term = (300 - df["front_distance"].clip(0, 300)) / 60.0
    nuclear_term = df["has_nuclear"]
    night_term = df["este_noapte"]
    weather_term = 1 - df["vreme_severa"]

    score = (
        w_dist * dist_front_term
        + w_infra * infrastructure_term
        + w_front * front_distance_term
        + w_nuclear * nuclear_term
        + w_night * night_term
        + w_weather * weather_term
    )

    thr = score.quantile(quantile)
    label = (score >= thr).astype(int)
    return score, label


def evaluate_config(df, w_dist, w_infra, w_front, w_nuclear, w_night, w_weather, quantile):
    """Antrenează modelul pentru o configurație și întoarce metricile."""
    scor_risc, risc_inalt = build_risk_label(
        df,
        w_dist=w_dist,
        w_infra=w_infra,
        w_front=w_front,
        w_nuclear=w_nuclear,
        w_night=w_night,
        w_weather=w_weather,
        quantile=quantile,
    )

    df = df.copy()
    df["scor_risc_heuristic"] = scor_risc
    df["risc_inalt"] = risc_inalt

   
    df["scor_infrastructura_total"] = (
        df["energy_score"] + df["military_score"] + df["logistics_score"]
    )

    enc_arma = LabelEncoder()
    enc_loc = LabelEncoder()

    df["arma_cod"] = enc_arma.fit_transform(df["model"].fillna("Unknown"))
    df["loc_cod"] = enc_loc.fit_transform(df["launch_place"].fillna("Unknown"))

    X = df[
        [
            "ora_lansarii",
            "este_noapte",
            "este_sezon_rece",
            "vreme_severa",
            "arma_cod",
            "loc_cod",
            "scor_infrastructura_total",
            "has_nuclear",
            "front_distance",
        ]
    ]
    y = df["risc_inalt"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )

    model = HistGradientBoostingClassifier(
        learning_rate=0.1,
        max_depth=8,
        max_iter=300,
        min_samples_leaf=20,
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_proba = model.predict_proba(X_test)[:, 1]

   
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

    return {
        "w_dist": w_dist,
        "w_infra": w_infra,
        "w_front": w_front,
        "w_nuclear": w_nuclear,
        "w_night": w_night,
        "w_weather": w_weather,
        "quantile": quantile,
        "auc": auc,
        "best_thr": best_thr,
        "best_acc": best_acc,
        "best_f1": best_f1,
    }


def main():
    cale_atacuri = "20000_randuri_atacuri_ucraina.csv"
    cale_strategica = "dataset_strategic_id.csv"

    print("📥 Încarc datele...")
    df_atacuri = pd.read_csv(cale_atacuri)
    df_strategic = pd.read_csv(cale_strategica)

    df_atacuri = df_atacuri.rename(columns={" atac": "atac"})
    df = pd.merge(
        df_atacuri,
        df_strategic,
        left_on="regiune_standard",
        right_on="regiune",
        how="inner",
    )

    print("Dimensiunea setului de date după merge:", df.shape)

    
    quantiles = [0.70]             
    w_dists = [0.5, 1.0]            
    w_infras = [0.5, 1.0]           
    w_fronts = [0.5, 1.0]           
    w_nuclears = [1.5, 2.0]         
    w_nights = [1.0, 2.0]          
    w_weathers = [1.0, 1.5]        

    configs = list(
        itertools.product(
            quantiles,
            w_dists,
            w_infras,
            w_fronts,
            w_nuclears,
            w_nights,
            w_weathers,
        )
    )

    print(f"Voi evalua {len(configs)} configurații (poate dura câteva zeci de secunde)...")

    results = []
    for (
        q,
        wd,
        wi,
        wf,
        wnuc,
        wnight,
        wweather,
    ) in configs:
        res = evaluate_config(
            df,
            w_dist=wd,
            w_infra=wi,
            w_front=wf,
            w_nuclear=wnuc,
            w_night=wnight,
            w_weather=wweather,
            quantile=q,
        )
        results.append(res)

    results_df = pd.DataFrame(results)

   
    results_df = results_df.sort_values(
        by=["auc", "best_f1"], ascending=False
    ).reset_index(drop=True)

    print("\n=== Top 10 configurații după AUC + F1 ===")
    print(
        results_df.head(10)[
            [
                "auc",
                "best_f1",
                "best_acc",
                "best_thr",
                "quantile",
                "w_dist",
                "w_infra",
                "w_front",
                "w_nuclear",
                "w_night",
                "w_weather",
            ]
        ]
    )


if __name__ == "__main__":
    main()


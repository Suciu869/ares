import pandas as pd
from sklearn.metrics import roc_auc_score


def main():
    cale_atacuri = "20000_randuri_atacuri_ucraina.csv"
    cale_strategica = "dataset_strategic_id.csv"

    print(" Încarc CSV-urile...")
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


    print("\n=== Distribuție label `atac` înainte de orice echilibrare ===")
    print(df["atac"].value_counts(normalize=True))

    y = df["atac"].astype(int)

 
    numeric_cols = [
        "ora_lansarii",
        "este_sezon_rece",
        "este_noapte",
        "vreme_severa",
        "distanta_front_km",
        "scor_infrastructura",
        "energy_score",
        "military_score",
        "logistics_score",
        "front_distance",
        "has_nuclear",
    ]

    print("\n=== Analiză univariată numerică (mean pe clasă + ROC-AUC per feature) ===")
    for col in numeric_cols:
        if col not in df.columns:
            continue
        x = df[col]
      
        if x.nunique() <= 1:
            continue

        mean_0 = x[y == 0].mean()
        mean_1 = x[y == 1].mean()

        try:
            auc = roc_auc_score(y, x)
        except ValueError:
            auc = float("nan")

        print(f"\nFeature: {col}")
        print(f"  mean(atac=0): {mean_0:.3f}")
        print(f"  mean(atac=1): {mean_1:.3f}")
        print(f"  ROC-AUC (univariat): {auc:.3f}")

 
    categorical_cols = [
        "model",
        "launch_place",
        "regiune_standard",
        "target_main",
        "target",
    ]

    print("\n=== Info rapide pentru feature-uri categorice ===")
    for col in categorical_cols:
        if col not in df.columns:
            continue
        vc = df[col].value_counts().head(5)
        print(f"\nFeature: {col}")
        print(f"  număr valori distincte: {df[col].nunique()}")
        print("  Top 5 valori (proporție):")
        print((vc / len(df)).round(3))


if __name__ == "__main__":
    main()


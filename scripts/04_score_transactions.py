from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

INPUT_PATH = PROCESSED_DATA_DIR / "transactions_clean.csv"
OUTPUT_PATH = PROCESSED_DATA_DIR / "transactions_scored.csv"


def load_clean_data() -> pd.DataFrame:
    """Load cleaned transaction data."""
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Clean data file not found: {INPUT_PATH}. "
            "Run scripts/03_clean_transactions.py first."
        )

    df = pd.read_csv(INPUT_PATH)

    print(f"Loaded clean data from: {INPUT_PATH}")
    print(f"Input shape: {df.shape}")

    return df


def add_rule_based_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a rule-based anomaly score.

    This is a heuristic risk scoring approach. It does not represent a supervised
    fraud prediction model because the dataset does not contain confirmed fraud labels.
    """
    df = df.copy()

    amount_p95 = df["transaction_amount"].quantile(0.95)
    amount_p99 = df["transaction_amount"].quantile(0.99)
    duration_p95 = df["transaction_duration"].quantile(0.95)
    balance_p05 = df["account_balance"].quantile(0.05)

    df["risk_score"] = 0

    df.loc[df["transaction_amount"] >= amount_p95, "risk_score"] += 30
    df.loc[df["transaction_amount"] >= amount_p99, "risk_score"] += 20
    df.loc[df["login_attempts"] > 1, "risk_score"] += 20
    df.loc[df["transaction_duration"] >= duration_p95, "risk_score"] += 20
    df.loc[df["account_balance"] <= balance_p05, "risk_score"] += 20
    df.loc[df["transaction_hour"].between(0, 5), "risk_score"] += 10
    df.loc[df["minutes_since_previous_transaction"] <= 10, "risk_score"] += 20

    df["anomaly_flag"] = (df["risk_score"] >= 60).astype(int)

    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[-1, 29, 59, float("inf")],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    return df


def save_scored_data(df: pd.DataFrame) -> None:
    """Save scored transaction data."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Scored data saved to: {OUTPUT_PATH}")
    print(f"Output shape: {df.shape}")

    print("\nRisk level distribution:")
    print(df["risk_level"].value_counts())

    print("\nAnomaly flag distribution:")
    print(df["anomaly_flag"].value_counts())


def main() -> None:
    df = load_clean_data()
    df = add_rule_based_risk_score(df)
    save_scored_data(df)


if __name__ == "__main__":
    main()
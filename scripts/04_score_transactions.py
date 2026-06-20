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
    Add rule-based risk score, suspicious flag, risk level, and risk reason codes.

    The score is heuristic and does not represent confirmed fraud prediction.
    Risk reasons explain why a transaction received risk points.
    """
    df = df.copy()

    amount_p95 = df["transaction_amount"].quantile(0.95)
    amount_p99 = df["transaction_amount"].quantile(0.99)
    duration_p95 = df["transaction_duration"].quantile(0.95)
    balance_p05 = df["account_balance"].quantile(0.05)

    df["risk_score"] = 0
    df["risk_reasons"] = ""

    def add_risk(condition: pd.Series, points: int, reason: str) -> None:
        df.loc[condition, "risk_score"] += points

        df.loc[condition, "risk_reasons"] = df.loc[
            condition,
            "risk_reasons"
        ].apply(
            lambda existing: reason if existing == "" else f"{existing}, {reason}"
        )

    add_risk(
        df["transaction_amount"] >= amount_p95,
        30,
        "high_amount_p95",
    )

    add_risk(
        df["transaction_amount"] >= amount_p99,
        20,
        "very_high_amount_p99",
    )

    add_risk(
        df["login_attempts"] > 1,
        20,
        "multiple_login_attempts",
    )

    add_risk(
        df["transaction_duration"] >= duration_p95,
        20,
        "long_transaction_duration",
    )

    add_risk(
        df["account_balance"] <= balance_p05,
        20,
        "low_account_balance",
    )

    add_risk(
        df["transaction_hour"].between(0, 5),
        10,
        "night_transaction",
    )

    add_risk(
        df["minutes_since_previous_transaction"] <= 10,
        20,
        "short_interval_since_previous_transaction",
    )

    df["risk_score"] = df["risk_score"].clip(upper=100)

    df["suspicious_flag"] = (df["risk_score"] >= 60).astype(int)

    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[-1, 29, 59, 100],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    df["risk_reasons"] = df["risk_reasons"].replace("", "no_risk_rule_triggered")

    return df


def save_scored_data(df: pd.DataFrame) -> None:
    """Save scored transaction data."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Scored data saved to: {OUTPUT_PATH}")
    print(f"Output shape: {df.shape}")

    print("\nRisk level distribution:")
    print(df["risk_level"].value_counts())

    print("\nSuspicious flag distribution:")
    print(df["suspicious_flag"].value_counts())

    print("\nTop risk reasons:")
    print(df["risk_reasons"].value_counts().head(10))


def main() -> None:
    df = load_clean_data()
    df = add_rule_based_risk_score(df)
    save_scored_data(df)


if __name__ == "__main__":
    main()
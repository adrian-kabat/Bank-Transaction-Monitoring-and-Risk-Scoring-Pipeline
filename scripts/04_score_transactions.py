from pathlib import Path

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

INPUT_PATH = PROCESSED_DATA_DIR / "transactions_clean.csv"
OUTPUT_PATH = PROCESSED_DATA_DIR / "transactions_scored.csv"
CONFIG_PATH = PROJECT_ROOT / "config" / "risk_rules.yaml"

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

def load_risk_rules() -> dict:
    """Load rule-based risk scoring configuration from YAML file."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

def add_rule_based_risk_score(df: pd.DataFrame, rules: dict) -> pd.DataFrame:
    """
    Add rule-based risk score, suspicious flag, risk level, and risk reason codes.

    The score is heuristic and does not represent confirmed fraud prediction.
    Risk reasons explain why a transaction received risk points.
    """
    df = df.copy()

    amount_p95 = df["transaction_amount"].quantile(
        rules["amount"]["high_amount_quantile"]
    )

    amount_p99 = df["transaction_amount"].quantile(
        rules["amount"]["very_high_amount_quantile"]
    )

    duration_p95 = df["transaction_duration"].quantile(
        rules["transaction_duration"]["long_duration_quantile"]
    )

    balance_p05 = df["account_balance"].quantile(
        rules["account_balance"]["low_balance_quantile"]
    )

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
        rules["amount"]["high_amount_points"],
        "high_amount_p95",
    )

    add_risk(
        df["transaction_amount"] >= amount_p99,
        rules["amount"]["very_high_amount_points"],
        "very_high_amount_p99",
    )

    add_risk(
        df["login_attempts"] > rules["login_attempts"]["multiple_login_attempts_threshold"],
        rules["login_attempts"]["multiple_login_attempts_points"],
        "multiple_login_attempts",
    )

    add_risk(
        df["transaction_duration"] >= duration_p95,
        rules["transaction_duration"]["long_duration_points"],
        "long_transaction_duration",
    )

    add_risk(
        df["account_balance"] <= balance_p05,
        rules["account_balance"]["low_balance_points"],
        "low_account_balance",
    )

    add_risk(
        df["transaction_hour"].between(
            rules["transaction_hour"]["night_start_hour"],
            rules["transaction_hour"]["night_end_hour"],
        ),
        rules["transaction_hour"]["night_transaction_points"],
        "night_transaction",
    )

    if rules["transaction_frequency"]["enabled"]:
        add_risk(
            df["minutes_since_previous_transaction"]
            <= rules["transaction_frequency"]["short_interval_minutes"],
            rules["transaction_frequency"]["short_interval_points"],
            "short_interval_since_previous_transaction",
        )

    df["risk_score"] = df["risk_score"].clip(
        upper=rules["classification"]["max_risk_score"]
    )

    df["suspicious_flag"] = (
        df["risk_score"] >= rules["classification"]["suspicious_threshold"]
    ).astype(int)

    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[
            -1,
            rules["classification"]["low_risk_max"],
            rules["classification"]["medium_risk_max"],
            rules["classification"]["max_risk_score"],
        ],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    df["risk_reasons"] = df["risk_reasons"].replace(
        "",
        "no_risk_rule_triggered",
    )

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
    rules = load_risk_rules()
    df = load_clean_data()
    df = add_rule_based_risk_score(df, rules)
    save_scored_data(df)


if __name__ == "__main__":
    main()
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCORED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "transactions_scored.csv"


def load_transactions() -> pd.DataFrame:
    """Load scored transaction data used by the mock API."""
    if not SCORED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Scored data file not found: {SCORED_DATA_PATH}. "
            "Run scripts/04_score_transactions.py first."
        )

    df = pd.read_csv(SCORED_DATA_PATH)

    return df


def get_transactions(
    limit: int = 100,
    risk_level: str | None = None,
    channel: str | None = None,
) -> list[dict]:
    """Return transaction records with optional filters."""
    df = load_transactions()

    if risk_level:
        df = df[df["risk_level"].str.lower() == risk_level.lower()]

    if channel:
        df = df[df["channel"].str.lower() == channel.lower()]

    df = df.head(limit)

    return df.to_dict(orient="records")


def get_accounts() -> list[dict]:
    """Return unique account records."""
    df = load_transactions()

    accounts = (
        df[
            [
                "account_id",
                "customer_age",
                "customer_occupation",
            ]
        ]
        .drop_duplicates()
        .sort_values("account_id")
    )

    return accounts.to_dict(orient="records")


def get_merchants() -> list[dict]:
    """Return unique merchant records."""
    df = load_transactions()

    merchants = (
        df[["merchant_id"]]
        .drop_duplicates()
        .sort_values("merchant_id")
    )

    return merchants.to_dict(orient="records")


def get_channels() -> list[dict]:
    """Return unique transaction channels."""
    df = load_transactions()

    channels = (
        df[["channel"]]
        .drop_duplicates()
        .sort_values("channel")
    )

    return channels.to_dict(orient="records")


def get_api_summary() -> dict:
    """Return basic API-level summary statistics."""
    df = load_transactions()

    return {
        "transaction_count": int(len(df)),
        "account_count": int(df["account_id"].nunique()),
        "merchant_count": int(df["merchant_id"].nunique()),
        "channel_count": int(df["channel"].nunique()),
        "suspicious_transaction_count": int(df["suspicious_flag"].sum()),
        "average_risk_score": round(float(df["risk_score"].mean()), 2),
    }
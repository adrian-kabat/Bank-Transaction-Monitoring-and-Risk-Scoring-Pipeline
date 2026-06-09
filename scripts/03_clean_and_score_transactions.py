from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


COLUMN_MAPPING = {
    "TransactionID": "transaction_id",
    "AccountID": "account_id",
    "TransactionAmount": "transaction_amount",
    "TransactionDate": "transaction_date",
    "TransactionType": "transaction_type",
    "Location": "location",
    "DeviceID": "device_id",
    "IP Address": "ip_address",
    "MerchantID": "merchant_id",
    "Channel": "channel",
    "CustomerAge": "customer_age",
    "CustomerOccupation": "customer_occupation",
    "TransactionDuration": "transaction_duration",
    "LoginAttempts": "login_attempts",
    "AccountBalance": "account_balance",
    "PreviousTransactionDate": "previous_transaction_date",
}


REQUIRED_COLUMNS = list(COLUMN_MAPPING.values())


def find_csv_file() -> Path:
    """Find the first CSV file in the raw data directory."""
    csv_files = list(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV file found in {RAW_DATA_DIR}. "
            "Run scripts/00_download_data.py first."
        )

    if len(csv_files) > 1:
        print("Multiple CSV files found. Using the first one:")
        for file in csv_files:
            print(f"- {file}")

    return csv_files[0]


def load_raw_data() -> pd.DataFrame:
    """Load raw transaction data from CSV."""
    csv_path = find_csv_file()
    df = pd.read_csv(csv_path)

    print(f"Loaded raw data from: {csv_path}")
    print(f"Raw shape: {df.shape}")

    return df


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Rename raw columns to snake_case analytical column names."""
    df = df.rename(columns=COLUMN_MAPPING)

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns after renaming: {missing_columns}")

    return df


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Clean text columns by trimming whitespace and standardizing casing where appropriate."""
    text_columns = [
        "transaction_id",
        "account_id",
        "transaction_type",
        "location",
        "device_id",
        "ip_address",
        "merchant_id",
        "channel",
        "customer_occupation",
    ]

    for column in text_columns:
        df[column] = df[column].astype(str).str.strip()

    df["transaction_type"] = df["transaction_type"].str.title()
    df["channel"] = df["channel"].str.title()
    df["customer_occupation"] = df["customer_occupation"].str.title()
    df["location"] = df["location"].str.title()

    return df


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse transaction date columns to datetime."""
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["previous_transaction_date"] = pd.to_datetime(
        df["previous_transaction_date"],
        errors="coerce",
    )

    if df["transaction_date"].isna().any():
        raise ValueError("Some transaction_date values could not be parsed.")

    if df["previous_transaction_date"].isna().any():
        raise ValueError("Some previous_transaction_date values could not be parsed.")

    return df


def validate_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Validate numerical fields and remove impossible records if present."""
    numeric_columns = [
        "transaction_amount",
        "customer_age",
        "transaction_duration",
        "login_attempts",
        "account_balance",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    before_rows = len(df)

    df = df.dropna(subset=numeric_columns)
    df = df[df["transaction_amount"] > 0]
    df = df[df["customer_age"].between(0, 120)]
    df = df[df["transaction_duration"] >= 0]
    df = df[df["login_attempts"] >= 0]
    df = df[df["account_balance"] >= 0]

    removed_rows = before_rows - len(df)

    if removed_rows > 0:
        print(f"Removed {removed_rows} rows with invalid numeric values.")

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate transactions based on transaction_id."""
    before_rows = len(df)
    df = df.drop_duplicates(subset=["transaction_id"])
    removed_rows = before_rows - len(df)

    if removed_rows > 0:
        print(f"Removed {removed_rows} duplicated transactions.")

    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create analytical features used for anomaly scoring and dashboarding."""
    df["transaction_hour"] = df["transaction_date"].dt.hour
    df["transaction_date_only"] = df["transaction_date"].dt.date
    df["transaction_year"] = df["transaction_date"].dt.year
    df["transaction_month"] = df["transaction_date"].dt.month
    df["transaction_day_of_week"] = df["transaction_date"].dt.day_name()
    df["is_weekend"] = df["transaction_date"].dt.dayofweek.isin([5, 6]).astype(int)

    df["minutes_since_previous_transaction"] = (
        df["transaction_date"] - df["previous_transaction_date"]
    ).dt.total_seconds() / 60

    df["minutes_since_previous_transaction"] = (
        df["minutes_since_previous_transaction"]
        .clip(lower=0)
        .round(2)
    )

    df["transaction_count"] = 1

    return df


def add_anomaly_score(df: pd.DataFrame) -> pd.DataFrame:
    """Create rule-based anomaly score and risk level."""
    amount_p95 = df["transaction_amount"].quantile(0.95)
    amount_p99 = df["transaction_amount"].quantile(0.99)
    duration_p95 = df["transaction_duration"].quantile(0.95)
    balance_p05 = df["account_balance"].quantile(0.05)

    df["anomaly_score"] = 0

    df.loc[df["transaction_amount"] >= amount_p95, "anomaly_score"] += 30
    df.loc[df["transaction_amount"] >= amount_p99, "anomaly_score"] += 20
    df.loc[df["login_attempts"] > 1, "anomaly_score"] += 20
    df.loc[df["transaction_duration"] >= duration_p95, "anomaly_score"] += 20
    df.loc[df["account_balance"] <= balance_p05, "anomaly_score"] += 20
    df.loc[df["transaction_hour"].between(0, 5), "anomaly_score"] += 10
    df.loc[df["minutes_since_previous_transaction"] <= 10, "anomaly_score"] += 20

    df["anomaly_flag"] = (df["anomaly_score"] >= 60).astype(int)

    df["risk_level"] = pd.cut(
        df["anomaly_score"],
        bins=[-1, 29, 59, float("inf")],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    return df


def save_processed_data(df: pd.DataFrame) -> None:
    """Save cleaned and scored transaction data."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_path = PROCESSED_DATA_DIR / "transactions_scored.csv"
    df.to_csv(output_path, index=False)

    print(f"Processed data saved to: {output_path}")
    print(f"Processed shape: {df.shape}")

    print("\nRisk level distribution:")
    print(df["risk_level"].value_counts())

    print("\nAnomaly flag distribution:")
    print(df["anomaly_flag"].value_counts())


def main() -> None:
    df = load_raw_data()
    df = standardize_column_names(df)
    df = clean_text_columns(df)
    df = parse_dates(df)
    df = validate_numeric_columns(df)
    df = remove_duplicates(df)
    df = add_features(df)
    df = add_anomaly_score(df)
    save_processed_data(df)


if __name__ == "__main__":
    main()
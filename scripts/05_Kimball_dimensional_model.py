from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "transactions_scored.csv"
WAREHOUSE_DIR = PROJECT_ROOT / "warehouse"
WAREHOUSE_PATH = WAREHOUSE_DIR / "transaction_monitoring.db"


def load_processed_data() -> pd.DataFrame:
    """Load cleaned and scored transaction data."""
    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Processed data file not found: {PROCESSED_DATA_PATH}. "
            "Run scripts/04_score_transactions.py first."
        )

    df = pd.read_csv(PROCESSED_DATA_PATH)

    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["previous_transaction_date"] = pd.to_datetime(df["previous_transaction_date"])
    df["transaction_date_only"] = pd.to_datetime(df["transaction_date_only"]).dt.date

    print(f"Loaded processed data from: {PROCESSED_DATA_PATH}")
    print(f"Processed shape: {df.shape}")

    return df


def build_dim_account(df: pd.DataFrame) -> pd.DataFrame:
    """Build account/customer dimension."""
    dim_account = (
        df[
            [
                "account_id",
                "customer_age",
                "customer_occupation",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    dim_account.insert(0, "account_key", range(1, len(dim_account) + 1))

    return dim_account


def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    """Build date dimension based on transaction dates."""
    dates = pd.DataFrame({
        "date": pd.to_datetime(df["transaction_date_only"].unique())
    })

    dates = dates.sort_values("date").reset_index(drop=True)

    dates["date_key"] = dates["date"].dt.strftime("%Y%m%d").astype(int)
    dates["year"] = dates["date"].dt.year
    dates["quarter"] = dates["date"].dt.quarter
    dates["month"] = dates["date"].dt.month
    dates["month_name"] = dates["date"].dt.month_name()
    dates["day"] = dates["date"].dt.day
    dates["day_of_week"] = dates["date"].dt.day_name()
    dates["day_of_week_number"] = dates["date"].dt.dayofweek + 1
    dates["is_weekend"] = dates["date"].dt.dayofweek.isin([5, 6]).astype(int)

    dim_date = dates[
        [
            "date_key",
            "date",
            "year",
            "quarter",
            "month",
            "month_name",
            "day",
            "day_of_week",
            "day_of_week_number",
            "is_weekend",
        ]
    ]

    return dim_date


def build_simple_dimension(
    df: pd.DataFrame,
    source_column: str,
    key_column: str,
    value_column: str,
) -> pd.DataFrame:
    """Build a simple one-column dimension with a surrogate key."""
    dimension = (
        df[[source_column]]
        .drop_duplicates()
        .sort_values(source_column)
        .reset_index(drop=True)
        .rename(columns={source_column: value_column})
    )

    dimension.insert(0, key_column, range(1, len(dimension) + 1))

    return dimension


def build_dimensions(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Build all Kimball-style dimension tables."""
    dimensions = {
        "dim_account": build_dim_account(df),
        "dim_date": build_dim_date(df),
        "dim_merchant": build_simple_dimension(
            df=df,
            source_column="merchant_id",
            key_column="merchant_key",
            value_column="merchant_id",
        ),
        "dim_channel": build_simple_dimension(
            df=df,
            source_column="channel",
            key_column="channel_key",
            value_column="channel",
        ),
        "dim_location": build_simple_dimension(
            df=df,
            source_column="location",
            key_column="location_key",
            value_column="location",
        ),
        "dim_device": build_simple_dimension(
            df=df,
            source_column="device_id",
            key_column="device_key",
            value_column="device_id",
        ),
        "dim_transaction_type": build_simple_dimension(
            df=df,
            source_column="transaction_type",
            key_column="transaction_type_key",
            value_column="transaction_type",
        ),
    }

    return dimensions


def build_fact_transactions(
    df: pd.DataFrame,
    dimensions: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Build transaction fact table with foreign keys to dimensions."""
    fact = df.copy()

    fact = fact.merge(
        dimensions["dim_account"],
        on=["account_id", "customer_age", "customer_occupation"],
        how="left",
    )

    fact["date_key"] = pd.to_datetime(fact["transaction_date_only"]).dt.strftime("%Y%m%d").astype(int)

    fact = fact.merge(
        dimensions["dim_merchant"],
        on="merchant_id",
        how="left",
    )

    fact = fact.merge(
        dimensions["dim_channel"],
        on="channel",
        how="left",
    )

    fact = fact.merge(
        dimensions["dim_location"],
        on="location",
        how="left",
    )

    fact = fact.merge(
        dimensions["dim_device"],
        on="device_id",
        how="left",
    )

    fact = fact.merge(
        dimensions["dim_transaction_type"],
        on="transaction_type",
        how="left",
    )

    fact.insert(0, "transaction_key", range(1, len(fact) + 1))

    fact_transactions = fact[
        [
            "transaction_key",
            "transaction_id",
            "account_key",
            "date_key",
            "merchant_key",
            "channel_key",
            "location_key",
            "device_key",
            "transaction_type_key",
            "transaction_date",
            "previous_transaction_date",
            "transaction_amount",
            "transaction_duration",
            "login_attempts",
            "account_balance",
            "minutes_since_previous_transaction",
            "transaction_hour",
            "transaction_count",
            "risk_score",
            "anomaly_flag",
            "risk_level",
        ]
    ]

    return fact_transactions


def save_tables_to_sqlite(
    dimensions: dict[str, pd.DataFrame],
    fact_transactions: pd.DataFrame,
) -> None:
    """Save dimensions and fact table to a local SQLite warehouse."""
    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(WAREHOUSE_PATH) as connection:
        for table_name, table_df in dimensions.items():
            table_df.to_sql(
                table_name,
                connection,
                if_exists="replace",
                index=False,
            )
            print(f"Saved table: {table_name} ({len(table_df)} rows)")

        fact_transactions.to_sql(
            "fact_transactions",
            connection,
            if_exists="replace",
            index=False,
        )
        print(f"Saved table: fact_transactions ({len(fact_transactions)} rows)")

    print(f"\nSQLite warehouse created at: {WAREHOUSE_PATH}")


def validate_model(
    dimensions: dict[str, pd.DataFrame],
    fact_transactions: pd.DataFrame,
) -> None:
    """Run basic validation checks for the dimensional model."""
    print("\nModel validation:")

    print(f"- fact_transactions rows: {len(fact_transactions)}")
    print(f"- unique transaction_id values: {fact_transactions['transaction_id'].nunique()}")

    duplicate_transactions = fact_transactions["transaction_id"].duplicated().sum()
    print(f"- duplicated transaction_id values: {duplicate_transactions}")

    foreign_keys = [
        ("account_key", "dim_account"),
        ("date_key", "dim_date"),
        ("merchant_key", "dim_merchant"),
        ("channel_key", "dim_channel"),
        ("location_key", "dim_location"),
        ("device_key", "dim_device"),
        ("transaction_type_key", "dim_transaction_type"),
    ]

    for key_column, dimension_name in foreign_keys:
        missing_keys = fact_transactions[key_column].isna().sum()
        print(f"- missing {key_column}: {missing_keys}")

    print("\nDimension sizes:")
    for table_name, table_df in dimensions.items():
        print(f"- {table_name}: {len(table_df)} rows")


def main() -> None:
    df = load_processed_data()
    dimensions = build_dimensions(df)
    fact_transactions = build_fact_transactions(df, dimensions)

    validate_model(dimensions, fact_transactions)
    save_tables_to_sqlite(dimensions, fact_transactions)


if __name__ == "__main__":
    main()
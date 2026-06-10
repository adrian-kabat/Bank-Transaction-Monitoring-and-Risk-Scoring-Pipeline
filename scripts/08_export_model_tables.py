from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WAREHOUSE_PATH = PROJECT_ROOT / "warehouse" / "transaction_monitoring.db"
MODEL_DATA_DIR = PROJECT_ROOT / "data" / "model"


TABLES = [
    "dim_account",
    "dim_date",
    "dim_merchant",
    "dim_channel",
    "dim_location",
    "dim_device",
    "dim_transaction_type",
    "fact_transactions",
]


def export_table(connection: sqlite3.Connection, table_name: str) -> None:
    """Export one SQLite table to CSV."""
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql_query(query, connection)

    output_path = MODEL_DATA_DIR / f"{table_name}.csv"
    df.to_csv(output_path, index=False)

    print(f"Exported {table_name}: {len(df)} rows → {output_path}")


def main() -> None:
    if not WAREHOUSE_PATH.exists():
        raise FileNotFoundError(
            f"Warehouse database not found: {WAREHOUSE_PATH}. "
            "Run scripts/05_build_dimensional_model.py first."
        )

    MODEL_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(WAREHOUSE_PATH) as connection:
        for table_name in TABLES:
            export_table(connection, table_name)

    print("\nModel tables exported successfully.")


if __name__ == "__main__":
    main()
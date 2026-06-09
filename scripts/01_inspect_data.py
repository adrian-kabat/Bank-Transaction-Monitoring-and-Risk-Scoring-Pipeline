from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def find_csv_file() -> Path:
    """
    Find the first CSV file in the raw data directory.
    """
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


def inspect_data() -> None:
    """
    Print basic information about the raw dataset.
    """
    csv_path = find_csv_file()
    df = pd.read_csv(csv_path)

    print(f"\nFile: {csv_path}")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn names:")
    for column in df.columns:
        print(f"- {column}")

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isna().sum())

    print("\nFirst 5 rows:")
    print(df.head())


if __name__ == "__main__":
    inspect_data()
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR = PROJECT_ROOT / "reports"


def find_csv_file() -> Path:
    csv_files = list(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV file found in {RAW_DATA_DIR}. "
            "Run scripts/00_download_data.py first."
        )

    return csv_files[0]


def profile_raw_data() -> None:
    csv_path = find_csv_file()
    df = pd.read_csv(csv_path)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    profile = pd.DataFrame({
        "column_name": df.columns,
        "data_type": [df[column].dtype for column in df.columns],
        "missing_values": [df[column].isna().sum() for column in df.columns],
        "missing_pct": [round(df[column].isna().mean() * 100, 2) for column in df.columns],
        "unique_values": [df[column].nunique() for column in df.columns],
        "sample_values": [
            ", ".join(map(str, df[column].dropna().unique()[:5]))
            for column in df.columns
        ],
    })

    output_path = REPORTS_DIR / "raw_data_profile.csv"
    profile.to_csv(output_path, index=False)

    print(f"Raw data profile saved to: {output_path}")
    print("\nDataset shape:")
    print(df.shape)

    print("\nColumn profile:")
    print(profile)


if __name__ == "__main__":
    profile_raw_data()
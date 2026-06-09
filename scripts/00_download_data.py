from pathlib import Path
import shutil

import kagglehub


DATASET_ID = "valakhorasani/bank-transaction-dataset-for-fraud-detection"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def download_dataset() -> None:
    """
    Download the latest version of the Kaggle dataset using KaggleHub
    and copy CSV files to the project's data/raw directory.
    """
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    dataset_path = Path(kagglehub.dataset_download(DATASET_ID))

    print(f"Dataset downloaded by KaggleHub to: {dataset_path}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Raw data directory: {RAW_DATA_DIR}")

    csv_files = list(dataset_path.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in downloaded dataset directory: {dataset_path}"
        )

    for csv_file in csv_files:
        destination = RAW_DATA_DIR / csv_file.name
        shutil.copy2(csv_file, destination)
        print(f"Copied: {csv_file.name} → {destination}")

    print("\nRaw data is ready in data/raw/")


if __name__ == "__main__":
    download_dataset()
from pathlib import Path

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_OUTPUT_DIR = PROJECT_ROOT / "data" / "api"
API_TRANSACTIONS_PATH = API_OUTPUT_DIR / "transactions_from_api.csv"

API_BASE_URL = "http://127.0.0.1:8000"


def fetch_transactions(limit: int = 1000) -> pd.DataFrame:
    """Fetch transactions from the local mock API."""
    url = f"{API_BASE_URL}/transactions"

    response = requests.get(
        url,
        params={"limit": limit},
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    return pd.DataFrame(data)


def save_api_data(df: pd.DataFrame) -> None:
    """Save API response to a CSV file."""
    API_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(API_TRANSACTIONS_PATH, index=False)

    print(f"API data saved to: {API_TRANSACTIONS_PATH}")
    print(f"Shape: {df.shape}")


def main() -> None:
    df = fetch_transactions(limit=1000)
    save_api_data(df)


if __name__ == "__main__":
    main()
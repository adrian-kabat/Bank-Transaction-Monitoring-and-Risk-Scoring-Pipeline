from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SCORED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "transactions_scored.csv"
WAREHOUSE_PATH = PROJECT_ROOT / "warehouse" / "transaction_monitoring.db"
HTML_REPORT_PATH = PROJECT_ROOT / "reports" / "transaction_monitoring_report.html"


def test_scored_transactions_file_exists() -> None:
    assert SCORED_DATA_PATH.exists(), "Scored transactions file was not created."


def test_scored_transactions_contains_required_risk_columns() -> None:
    df = pd.read_csv(SCORED_DATA_PATH)

    required_columns = {
        "risk_score",
        "suspicious_flag",
        "risk_level",
        "risk_reasons",
    }

    missing_columns = required_columns - set(df.columns)

    assert not missing_columns, f"Missing columns: {missing_columns}"


def test_risk_score_is_within_expected_range() -> None:
    df = pd.read_csv(SCORED_DATA_PATH)

    assert df["risk_score"].between(0, 100).all()


def test_suspicious_flag_is_binary() -> None:
    df = pd.read_csv(SCORED_DATA_PATH)

    allowed_values = {0, 1}
    actual_values = set(df["suspicious_flag"].dropna().unique())

    assert actual_values.issubset(allowed_values)


def test_risk_level_has_expected_values() -> None:
    df = pd.read_csv(SCORED_DATA_PATH)

    allowed_values = {"Low", "Medium", "High"}
    actual_values = set(df["risk_level"].dropna().unique())

    assert actual_values.issubset(allowed_values)


def test_risk_reasons_are_not_empty() -> None:
    df = pd.read_csv(SCORED_DATA_PATH)

    assert df["risk_reasons"].notna().all()
    assert (df["risk_reasons"].astype(str).str.len() > 0).all()


def test_sqlite_warehouse_exists() -> None:
    assert WAREHOUSE_PATH.exists(), "SQLite warehouse was not created."


def test_sqlite_warehouse_contains_fact_and_dimension_tables() -> None:
    expected_tables = {
        "fact_transactions",
        "dim_account",
        "dim_date",
        "dim_merchant",
        "dim_channel",
        "dim_location",
        "dim_device",
        "dim_transaction_type",
    }

    with sqlite3.connect(WAREHOUSE_PATH) as connection:
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type = 'table';",
            connection,
        )

    actual_tables = set(tables["name"])

    missing_tables = expected_tables - actual_tables

    assert not missing_tables, f"Missing warehouse tables: {missing_tables}"


def test_html_report_exists() -> None:
    assert HTML_REPORT_PATH.exists(), "HTML report was not created."
from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SCORED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "transactions_scored.csv"
WAREHOUSE_PATH = PROJECT_ROOT / "warehouse" / "transaction_monitoring.db"
HTML_REPORT_PATH = PROJECT_ROOT / "reports" / "transaction_monitoring_report.html"
ANOMALY_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "transactions_with_anomaly_model.csv"
ANOMALY_COMPARISON_PATH = PROJECT_ROOT / "reports" / "anomaly_model_comparison.csv"
MODEL_FACT_TRANSACTIONS_PATH = PROJECT_ROOT / "data" / "model" / "fact_transactions.csv"

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

def test_transactions_with_anomaly_model_file_exists() -> None:
    assert ANOMALY_DATA_PATH.exists(), "Transactions with anomaly model file was not created."


def test_transactions_with_anomaly_model_contains_required_columns() -> None:
    df = pd.read_csv(ANOMALY_DATA_PATH)

    required_columns = {
        "ml_anomaly_score",
        "ml_anomaly_flag",
        "ml_anomaly_decision_score",
    }

    missing_columns = required_columns - set(df.columns)

    assert not missing_columns, f"Missing anomaly model columns: {missing_columns}"


def test_ml_anomaly_score_is_within_expected_range() -> None:
    df = pd.read_csv(ANOMALY_DATA_PATH)

    assert df["ml_anomaly_score"].between(0, 100).all()


def test_ml_anomaly_flag_is_binary() -> None:
    df = pd.read_csv(ANOMALY_DATA_PATH)

    allowed_values = {0, 1}
    actual_values = set(df["ml_anomaly_flag"].dropna().unique())

    assert actual_values.issubset(allowed_values)


def test_anomaly_model_comparison_file_exists() -> None:
    assert ANOMALY_COMPARISON_PATH.exists(), "Anomaly model comparison file was not created."


def test_anomaly_model_comparison_contains_expected_metrics() -> None:
    df = pd.read_csv(ANOMALY_COMPARISON_PATH)

    expected_metrics = {
        "total_transactions",
        "rule_based_suspicious_transactions",
        "ml_anomaly_transactions",
        "flagged_by_both_methods",
        "rule_based_only",
        "ml_only",
    }

    actual_metrics = set(df["metric"])

    missing_metrics = expected_metrics - actual_metrics

    assert not missing_metrics, f"Missing comparison metrics: {missing_metrics}"

def test_fact_transactions_contains_anomaly_model_columns() -> None:
    required_columns = {
        "ml_anomaly_score",
        "ml_anomaly_flag",
        "ml_anomaly_decision_score",
    }

    with sqlite3.connect(WAREHOUSE_PATH) as connection:
        fact_transactions = pd.read_sql_query(
            "SELECT * FROM fact_transactions LIMIT 1;",
            connection,
        )

    missing_columns = required_columns - set(fact_transactions.columns)

    assert not missing_columns, (
        f"Missing anomaly model columns in fact_transactions: {missing_columns}"
    )

def test_powerbi_fact_export_contains_anomaly_model_columns() -> None:
    assert MODEL_FACT_TRANSACTIONS_PATH.exists(), (
        "Power BI fact_transactions export was not created."
    )

    df = pd.read_csv(MODEL_FACT_TRANSACTIONS_PATH)

    required_columns = {
        "ml_anomaly_score",
        "ml_anomaly_flag",
        "ml_anomaly_decision_score",
    }

    missing_columns = required_columns - set(df.columns)

    assert not missing_columns, (
        f"Missing anomaly model columns in Power BI export: {missing_columns}"
    )
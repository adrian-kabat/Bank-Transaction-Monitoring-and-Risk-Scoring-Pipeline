from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WAREHOUSE_PATH = PROJECT_ROOT / "warehouse" / "transaction_monitoring.db"


QUERIES = {
    "basic_kpis": """
        SELECT
            COUNT(*) AS transaction_count,
            ROUND(SUM(transaction_amount), 2) AS total_transaction_amount,
            ROUND(AVG(transaction_amount), 2) AS average_transaction_amount,
            ROUND(AVG(account_balance), 2) AS average_account_balance,
            ROUND(AVG(risk_score), 2) AS average_risk_score
        FROM fact_transactions;
    """,
    "suspicious_kpis": """
        SELECT
            COUNT(*) AS transaction_count,
            SUM(anomaly_flag) AS suspicious_transaction_count,
            ROUND(
                100.0 * SUM(anomaly_flag) / COUNT(*),
                2
            ) AS suspicious_transaction_rate_pct,
            ROUND(
                SUM(CASE WHEN anomaly_flag = 1 THEN transaction_amount ELSE 0 END),
                2
            ) AS suspicious_transaction_amount
        FROM fact_transactions;
    """,
    "risk_by_channel": """
        SELECT
            c.channel,
            COUNT(*) AS transaction_count,
            SUM(f.anomaly_flag) AS suspicious_transaction_count,
            ROUND(
                100.0 * SUM(f.anomaly_flag) / COUNT(*),
                2
            ) AS suspicious_transaction_rate_pct,
            ROUND(AVG(f.risk_score), 2) AS average_risk_score
        FROM fact_transactions f
        JOIN dim_channel c
            ON f.channel_key = c.channel_key
        GROUP BY c.channel
        ORDER BY suspicious_transaction_rate_pct DESC;
    """,
}


def run_query(connection: sqlite3.Connection, query_name: str, query: str) -> None:
    print(f"\n=== {query_name} ===")
    result = pd.read_sql_query(query, connection)
    print(result)


def main() -> None:
    if not WAREHOUSE_PATH.exists():
        raise FileNotFoundError(
            f"Warehouse database not found: {WAREHOUSE_PATH}. "
            "Run scripts/04_build_dimensional_model.py first."
        )

    with sqlite3.connect(WAREHOUSE_PATH) as connection:
        for query_name, query in QUERIES.items():
            run_query(connection, query_name, query)


if __name__ == "__main__":
    main()
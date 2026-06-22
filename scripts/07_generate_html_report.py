from datetime import datetime
from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

WAREHOUSE_PATH = PROJECT_ROOT / "warehouse" / "transaction_monitoring.db"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORT_PATH = REPORTS_DIR / "transaction_monitoring_report.html"


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

    "rule_based_alert_kpis": """
        SELECT
            COUNT(*) AS transaction_count,
            SUM(suspicious_flag) AS rule_based_alert_count,
            ROUND(
                100.0 * SUM(suspicious_flag) / COUNT(*),
                2
            ) AS rule_based_alert_rate_pct,
            ROUND(
                SUM(CASE WHEN suspicious_flag = 1 THEN transaction_amount ELSE 0 END),
                2
            ) AS rule_based_alert_amount
        FROM fact_transactions;
    """,

    "ml_comparison_kpis": """
        SELECT
            SUM(ml_anomaly_flag) AS ml_anomaly_alert_count,
            ROUND(
                100.0 * SUM(ml_anomaly_flag) / COUNT(*),
                2
            ) AS ml_anomaly_rate_pct,
            SUM(
                CASE
                    WHEN suspicious_flag = 1 AND ml_anomaly_flag = 1
                    THEN 1 ELSE 0
                END
            ) AS flagged_by_both_methods,
            SUM(
                CASE
                    WHEN suspicious_flag = 1 AND ml_anomaly_flag = 0
                    THEN 1 ELSE 0
                END
            ) AS rule_based_only,
            SUM(
                CASE
                    WHEN suspicious_flag = 0 AND ml_anomaly_flag = 1
                    THEN 1 ELSE 0
                END
            ) AS ml_only,
            SUM(
                CASE
                    WHEN suspicious_flag = 1
                        AND ml_anomaly_flag = 1
                        AND risk_level = 'High'
                    THEN 1 ELSE 0
                END
            ) AS high_priority_review_queue
        FROM fact_transactions;
    """,

    "risk_exposure_kpis": """
        SELECT
            ROUND(
                SUM(transaction_amount * risk_score / 100.0),
                2
            ) AS risk_weighted_transaction_amount,
            ROUND(
                SUM(CASE WHEN suspicious_flag = 1 THEN transaction_amount ELSE 0 END),
                2
            ) AS rule_based_alert_amount,
            ROUND(
                SUM(CASE WHEN ml_anomaly_flag = 1 THEN transaction_amount ELSE 0 END),
                2
            ) AS ml_anomaly_amount,
            ROUND(
                SUM(
                    CASE
                        WHEN suspicious_flag = 1 AND ml_anomaly_flag = 1
                        THEN transaction_amount ELSE 0
                    END
                ),
                2
            ) AS both_methods_alert_amount
        FROM fact_transactions;
    """,

    "risk_level_distribution": """
        SELECT
            risk_level,
            COUNT(*) AS transaction_count,
            ROUND(SUM(transaction_amount), 2) AS total_transaction_amount,
            ROUND(AVG(transaction_amount), 2) AS average_transaction_amount,
            ROUND(AVG(risk_score), 2) AS average_risk_score,
            SUM(suspicious_flag) AS rule_based_alert_count,
            SUM(ml_anomaly_flag) AS ml_anomaly_alert_count
        FROM fact_transactions
        GROUP BY risk_level
        ORDER BY
            CASE risk_level
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
                ELSE 4
            END;
    """,

    "risk_by_channel": """
        SELECT
            c.channel,
            COUNT(*) AS transaction_count,
            ROUND(SUM(f.transaction_amount), 2) AS total_transaction_amount,
            SUM(f.suspicious_flag) AS rule_based_alert_count,
            ROUND(
                100.0 * SUM(f.suspicious_flag) / COUNT(*),
                2
            ) AS rule_based_alert_rate_pct,
            SUM(f.ml_anomaly_flag) AS ml_anomaly_alert_count,
            SUM(
                CASE
                    WHEN f.suspicious_flag = 1 AND f.ml_anomaly_flag = 1
                    THEN 1 ELSE 0
                END
            ) AS flagged_by_both_methods,
            ROUND(AVG(f.risk_score), 2) AS average_risk_score,
            ROUND(
                SUM(f.transaction_amount * f.risk_score / 100.0),
                2
            ) AS risk_weighted_transaction_amount
        FROM fact_transactions f
        JOIN dim_channel c
            ON f.channel_key = c.channel_key
        GROUP BY c.channel
        ORDER BY rule_based_alert_rate_pct DESC;
    """,

    "risk_by_transaction_type": """
        SELECT
            tt.transaction_type,
            COUNT(*) AS transaction_count,
            ROUND(SUM(f.transaction_amount), 2) AS total_transaction_amount,
            SUM(f.suspicious_flag) AS rule_based_alert_count,
            ROUND(
                100.0 * SUM(f.suspicious_flag) / COUNT(*),
                2
            ) AS rule_based_alert_rate_pct,
            SUM(f.ml_anomaly_flag) AS ml_anomaly_alert_count,
            ROUND(AVG(f.risk_score), 2) AS average_risk_score,
            ROUND(
                SUM(f.transaction_amount * f.risk_score / 100.0),
                2
            ) AS risk_weighted_transaction_amount
        FROM fact_transactions f
        JOIN dim_transaction_type tt
            ON f.transaction_type_key = tt.transaction_type_key
        GROUP BY tt.transaction_type
        ORDER BY rule_based_alert_rate_pct DESC;
    """,

    "risk_by_location": """
        SELECT
            l.location,
            COUNT(*) AS transaction_count,
            ROUND(SUM(f.transaction_amount), 2) AS total_transaction_amount,
            SUM(f.suspicious_flag) AS rule_based_alert_count,
            ROUND(
                100.0 * SUM(f.suspicious_flag) / COUNT(*),
                2
            ) AS rule_based_alert_rate_pct,
            SUM(f.ml_anomaly_flag) AS ml_anomaly_alert_count,
            ROUND(AVG(f.risk_score), 2) AS average_risk_score,
            ROUND(
                SUM(f.transaction_amount * f.risk_score / 100.0),
                2
            ) AS risk_weighted_transaction_amount
        FROM fact_transactions f
        JOIN dim_location l
            ON f.location_key = l.location_key
        GROUP BY l.location
        ORDER BY rule_based_alert_rate_pct DESC;
    """,

    "risk_reason_source": """
        SELECT
            risk_reasons
        FROM fact_transactions
        WHERE risk_reasons IS NOT NULL
            AND risk_reasons <> ''
            AND risk_reasons <> 'no_risk_rule_triggered'
            AND suspicious_flag = 1;
    """,

    "top_rule_based_alert_transactions": """
        SELECT
            f.transaction_id,
            f.transaction_date,
            a.account_id,
            m.merchant_id,
            c.channel,
            l.location,
            tt.transaction_type,
            ROUND(f.transaction_amount, 2) AS transaction_amount,
            f.login_attempts,
            f.transaction_duration,
            f.minutes_since_previous_transaction,
            f.account_balance,
            f.risk_score,
            f.risk_level,
            f.risk_reasons,
            f.ml_anomaly_score,
            f.ml_anomaly_flag
        FROM fact_transactions f
        JOIN dim_account a
            ON f.account_key = a.account_key
        JOIN dim_merchant m
            ON f.merchant_key = m.merchant_key
        JOIN dim_channel c
            ON f.channel_key = c.channel_key
        JOIN dim_location l
            ON f.location_key = l.location_key
        JOIN dim_transaction_type tt
            ON f.transaction_type_key = tt.transaction_type_key
        WHERE f.suspicious_flag = 1
        ORDER BY
            f.risk_score DESC,
            f.ml_anomaly_score DESC,
            f.transaction_amount DESC
        LIMIT 10;
    """,

    "risk_by_hour": """
        SELECT
            transaction_hour,
            COUNT(*) AS transaction_count,
            SUM(suspicious_flag) AS rule_based_alert_count,
            ROUND(
                100.0 * SUM(suspicious_flag) / COUNT(*),
                2
            ) AS rule_based_alert_rate_pct,
            SUM(ml_anomaly_flag) AS ml_anomaly_alert_count,
            ROUND(AVG(risk_score), 2) AS average_risk_score,
            ROUND(AVG(ml_anomaly_score), 2) AS average_ml_anomaly_score,
            ROUND(AVG(transaction_amount), 2) AS average_transaction_amount
        FROM fact_transactions
        GROUP BY transaction_hour
        ORDER BY transaction_hour;
    """,
}


SECTION_TITLES = {
    "rule_based_alert_kpis": "Rule-Based Alert KPIs",
    "ml_comparison_kpis": "Rule-Based vs ML Comparison",
    "risk_exposure_kpis": "Risk Exposure Summary",
    "risk_level_distribution": "Transactions by Risk Level",
    "top_risk_reasons": "Top Risk Reasons",
    "risk_by_channel": "Risk by Transaction Channel",
    "risk_by_transaction_type": "Risk by Transaction Type",
    "risk_by_location": "Risk by Location",
    "top_rule_based_alert_transactions": "Top Rule-Based Alert Transactions",
    "risk_by_hour": "Risk by Hour of Day",
}


COLUMN_LABELS = {
    "transaction_count": "Transaction Count",
    "total_transaction_amount": "Total Transaction Amount",
    "average_transaction_amount": "Average Transaction Amount",
    "average_account_balance": "Average Account Balance",
    "average_risk_score": "Average Risk Score",
    "rule_based_alert_count": "Rule-Based Alert Count",
    "rule_based_alert_rate_pct": "Rule-Based Alert Rate (%)",
    "rule_based_alert_amount": "Rule-Based Alert Amount",
    "ml_anomaly_alert_count": "ML Anomaly Alert Count",
    "ml_anomaly_rate_pct": "ML Anomaly Rate (%)",
    "flagged_by_both_methods": "Flagged by Both Methods",
    "rule_based_only": "Rule-Based Only",
    "ml_only": "ML Only",
    "high_priority_review_queue": "High Priority Review Queue",
    "risk_weighted_transaction_amount": "Risk-Weighted Transaction Amount",
    "ml_anomaly_amount": "ML Anomaly Amount",
    "both_methods_alert_amount": "Both Methods Alert Amount",
    "risk_level": "Risk Level",
    "risk_reason": "Risk Reason",
    "risk_reason_count": "Risk Reason Count",
    "risk_reason_share_pct": "Risk Reason Share (%)",
    "channel": "Channel",
    "transaction_type": "Transaction Type",
    "location": "Location",
    "transaction_hour": "Transaction Hour",
    "transaction_id": "Transaction ID",
    "transaction_date": "Transaction Date",
    "account_id": "Account ID",
    "merchant_id": "Merchant ID",
    "transaction_amount": "Transaction Amount",
    "login_attempts": "Login Attempts",
    "transaction_duration": "Transaction Duration",
    "minutes_since_previous_transaction": "Minutes Since Previous Transaction",
    "account_balance": "Account Balance",
    "risk_score": "Risk Score",
    "risk_reasons": "Risk Reasons",
    "ml_anomaly_score": "ML Anomaly Score",
    "ml_anomaly_flag": "ML Anomaly Flag",
    "average_ml_anomaly_score": "Average ML Anomaly Score",
}


def build_risk_reason_summary(source: pd.DataFrame) -> pd.DataFrame:
    """Create a frequency table of individual risk reason codes."""
    reasons: list[str] = []

    for value in source["risk_reasons"].dropna().astype(str):
        split_reasons = [reason.strip() for reason in value.split(",")]

        for reason in split_reasons:
            if reason and reason != "no_risk_rule_triggered":
                reasons.append(reason)

    if not reasons:
        return pd.DataFrame(
            columns=[
                "risk_reason",
                "risk_reason_count",
                "risk_reason_share_pct",
            ]
        )

    reason_counts = (
        pd.Series(reasons)
        .value_counts()
        .reset_index()
        .rename(
            columns={
                "index": "risk_reason",
                "count": "risk_reason_count",
            }
        )
    )

    if "risk_reason" not in reason_counts.columns:
        reason_counts.columns = ["risk_reason", "risk_reason_count"]

    rule_based_alerts_with_reasons = len(source)

    reason_counts["risk_reason_share_pct"] = (
        100.0
        * reason_counts["risk_reason_count"]
        / rule_based_alerts_with_reasons
    ).round(2)

    return reason_counts


def run_queries(connection: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    """Run SQL KPI queries and return results as pandas DataFrames."""
    results = {}

    for query_name, query in QUERIES.items():
        results[query_name] = pd.read_sql_query(query, connection)

    results["top_risk_reasons"] = build_risk_reason_summary(
        results["risk_reason_source"]
    )

    results.pop("risk_reason_source")

    return results


def format_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Format column names for presentation in the HTML report."""
    formatted_df = df.copy()

    formatted_df = formatted_df.rename(
        columns={
            column: COLUMN_LABELS.get(
                column,
                column.replace("_", " ").title(),
            )
            for column in formatted_df.columns
        }
    )

    return formatted_df


def dataframe_to_html_table(df: pd.DataFrame) -> str:
    """Convert a DataFrame to an HTML table with presentation-friendly names."""
    formatted_df = format_column_names(df)

    return formatted_df.to_html(
        index=False,
        border=0,
        classes="data-table",
        justify="center",
    )


def build_kpi_cards(
    basic_kpis: pd.DataFrame,
    rule_based_alert_kpis: pd.DataFrame,
    ml_comparison_kpis: pd.DataFrame,
    risk_exposure_kpis: pd.DataFrame,
) -> str:
    """Build HTML KPI cards from selected KPI query outputs."""
    basic = basic_kpis.iloc[0]
    rule_based = rule_based_alert_kpis.iloc[0]
    ml = ml_comparison_kpis.iloc[0]
    exposure = risk_exposure_kpis.iloc[0]

    cards = [
        ("Transactions", f"{int(basic['transaction_count']):,}"),
        ("Total Amount", f"{basic['total_transaction_amount']:,.2f}"),
        ("Rule-Based Alerts", f"{int(rule_based['rule_based_alert_count']):,}"),
        ("Rule-Based Alert Rate", f"{rule_based['rule_based_alert_rate_pct']:.2f}%"),
        ("ML Anomaly Alerts", f"{int(ml['ml_anomaly_alert_count']):,}"),
        ("ML Anomaly Rate", f"{ml['ml_anomaly_rate_pct']:.2f}%"),
        ("Flagged by Both Methods", f"{int(ml['flagged_by_both_methods']):,}"),
        ("High Priority Review Queue", f"{int(ml['high_priority_review_queue']):,}"),
        ("Risk-Weighted Amount", f"{exposure['risk_weighted_transaction_amount']:,.2f}"),
        ("Average Risk Score", f"{basic['average_risk_score']:.2f}"),
    ]

    cards_html = ""

    for label, value in cards:
        cards_html += f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
        """

    return f"""
        <section>
            <h2>Executive Summary</h2>
            <div class="kpi-grid">
                {cards_html}
            </div>
        </section>
    """


def build_html_report(results: dict[str, pd.DataFrame]) -> str:
    """Build the full HTML report."""
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    kpi_cards = build_kpi_cards(
        basic_kpis=results["basic_kpis"],
        rule_based_alert_kpis=results["rule_based_alert_kpis"],
        ml_comparison_kpis=results["ml_comparison_kpis"],
        risk_exposure_kpis=results["risk_exposure_kpis"],
    )

    section_order = [
        "rule_based_alert_kpis",
        "ml_comparison_kpis",
        "risk_exposure_kpis",
        "risk_level_distribution",
        "top_risk_reasons",
        "risk_by_channel",
        "risk_by_transaction_type",
        "risk_by_location",
        "top_rule_based_alert_transactions",
        "risk_by_hour",
    ]

    sections_html = ""

    for query_name in section_order:
        df = results[query_name]
        section_title = SECTION_TITLES.get(query_name, query_name)
        table_html = dataframe_to_html_table(df)

        sections_html += f"""
            <section>
                <h2>{section_title}</h2>
                <div class="table-wrapper">
                    {table_html}
                </div>
            </section>
        """

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Bank Transaction Monitoring Report</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 32px;
            background-color: #f7f8fa;
            color: #222;
        }}

        header {{
            margin-bottom: 28px;
        }}

        h1 {{
            margin-bottom: 6px;
            color: #1f2937;
        }}

        h2 {{
            margin-top: 32px;
            color: #1f2937;
            border-bottom: 2px solid #d1d5db;
            padding-bottom: 6px;
        }}

        p {{
            line-height: 1.5;
        }}

        .subtitle {{
            color: #4b5563;
            margin-top: 0;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 16px;
            margin-top: 18px;
        }}

        .kpi-card {{
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 16px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        }}

        .kpi-label {{
            font-size: 0.88rem;
            color: #6b7280;
            margin-bottom: 8px;
        }}

        .kpi-value {{
            font-size: 1.45rem;
            font-weight: bold;
            color: #111827;
        }}

        .table-wrapper {{
            overflow-x: auto;
            margin-top: 12px;
            background-color: #ffffff;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        }}

        table.data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}

        table.data-table th {{
            background-color: #f3f4f6;
            color: #111827;
            text-align: left;
            padding: 10px;
            border-bottom: 1px solid #d1d5db;
            white-space: nowrap;
        }}

        table.data-table td {{
            padding: 9px 10px;
            border-bottom: 1px solid #e5e7eb;
            vertical-align: top;
        }}

        table.data-table tr:nth-child(even) {{
            background-color: #f9fafb;
        }}

        .note {{
            margin-top: 32px;
            padding: 16px;
            background-color: #fff7ed;
            border-left: 4px solid #f97316;
            border-radius: 6px;
            color: #7c2d12;
        }}

        @media (max-width: 768px) {{
            body {{
                margin: 14px;
            }}

            .kpi-value {{
                font-size: 1.25rem;
            }}

            table.data-table {{
                font-size: 0.8rem;
            }}
        }}
    </style>
</head>

<body>
    <header>
        <h1>Bank Transaction Monitoring Report</h1>
        <p class="subtitle">
            Automated HTML report generated from the Kimball dimensional model.
            Generated at: {generated_at}
        </p>
    </header>

    {kpi_cards}

    {sections_html}

    <div class="note">
        <strong>Interpretation note:</strong>
        The dataset does not include confirmed fraud labels.
        Rule-based alerts and ML anomaly flags should be interpreted as transaction
        monitoring signals, not confirmed fraud predictions.
    </div>
</body>
</html>
"""

    return html


def save_report(html: str) -> None:
    """Save the HTML report to the reports directory."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(html, encoding="utf-8")

    print(f"HTML report saved to: {REPORT_PATH}")


def main() -> None:
    if not WAREHOUSE_PATH.exists():
        raise FileNotFoundError(
            f"Warehouse database not found: {WAREHOUSE_PATH}. "
            "Run scripts/10_run_pipeline.py first."
        )

    with sqlite3.connect(WAREHOUSE_PATH) as connection:
        results = run_queries(connection)

    html = build_html_report(results)
    save_report(html)


if __name__ == "__main__":
    main()
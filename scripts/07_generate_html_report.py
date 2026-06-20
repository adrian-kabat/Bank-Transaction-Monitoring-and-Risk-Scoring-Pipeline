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
    "suspicious_kpis": """
        SELECT
            COUNT(*) AS transaction_count,
            SUM(suspicious_flag) AS suspicious_transaction_count,
            ROUND(
                100.0 * SUM(suspicious_flag) / COUNT(*),
                2
            ) AS suspicious_transaction_rate_pct,
            ROUND(
                SUM(CASE WHEN suspicious_flag = 1 THEN transaction_amount ELSE 0 END),
                2
            ) AS suspicious_transaction_amount
        FROM fact_transactions;
    """,
    "risk_level_distribution": """
        SELECT
            risk_level,
            COUNT(*) AS transaction_count,
            ROUND(SUM(transaction_amount), 2) AS total_transaction_amount,
            ROUND(AVG(transaction_amount), 2) AS average_transaction_amount,
            ROUND(AVG(risk_score), 2) AS average_risk_score
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
            SUM(f.suspicious_flag) AS suspicious_transaction_count,
            ROUND(
                100.0 * SUM(f.suspicious_flag) / COUNT(*),
                2
            ) AS suspicious_transaction_rate_pct,
            ROUND(AVG(f.risk_score), 2) AS average_risk_score
        FROM fact_transactions f
        JOIN dim_channel c
            ON f.channel_key = c.channel_key
        GROUP BY c.channel
        ORDER BY suspicious_transaction_rate_pct DESC;
    """,
    "risk_by_transaction_type": """
        SELECT
            tt.transaction_type,
            COUNT(*) AS transaction_count,
            ROUND(SUM(f.transaction_amount), 2) AS total_transaction_amount,
            SUM(f.suspicious_flag) AS suspicious_transaction_count,
            ROUND(
                100.0 * SUM(f.suspicious_flag) / COUNT(*),
                2
            ) AS suspicious_transaction_rate_pct,
            ROUND(AVG(f.risk_score), 2) AS average_risk_score
        FROM fact_transactions f
        JOIN dim_transaction_type tt
            ON f.transaction_type_key = tt.transaction_type_key
        GROUP BY tt.transaction_type
        ORDER BY suspicious_transaction_rate_pct DESC;
    """,
    "risk_by_location": """
        SELECT
            l.location,
            COUNT(*) AS transaction_count,
            ROUND(SUM(f.transaction_amount), 2) AS total_transaction_amount,
            SUM(f.suspicious_flag) AS suspicious_transaction_count,
            ROUND(
                100.0 * SUM(f.suspicious_flag) / COUNT(*),
                2
            ) AS suspicious_transaction_rate_pct,
            ROUND(AVG(f.risk_score), 2) AS average_risk_score
        FROM fact_transactions f
        JOIN dim_location l
            ON f.location_key = l.location_key
        GROUP BY l.location
        ORDER BY suspicious_transaction_rate_pct DESC;
    """,
    "top_suspicious_transactions": """
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
            f.risk_level
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
            f.transaction_amount DESC
        LIMIT 10;
    """,
    "risk_by_hour": """
        SELECT
            transaction_hour,
            COUNT(*) AS transaction_count,
            SUM(suspicious_flag) AS suspicious_transaction_count,
            ROUND(
                100.0 * SUM(suspicious_flag) / COUNT(*),
                2
            ) AS suspicious_transaction_rate_pct,
            ROUND(AVG(risk_score), 2) AS average_risk_score,
            ROUND(AVG(transaction_amount), 2) AS average_transaction_amount
        FROM fact_transactions
        GROUP BY transaction_hour
        ORDER BY transaction_hour;
    """,
}


SECTION_TITLES = {
    "basic_kpis": "Basic transaction KPIs",
    "suspicious_kpis": "Suspicious transaction KPIs",
    "risk_level_distribution": "Transactions by risk level",
    "risk_by_channel": "Risk by transaction channel",
    "risk_by_transaction_type": "Risk by transaction type",
    "risk_by_location": "Risk by location",
    "top_suspicious_transactions": "Top suspicious transactions",
    "risk_by_hour": "Risk by hour of day",
}


def run_queries(connection: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    """Run SQL KPI queries and return results as pandas DataFrames."""
    results = {}

    for query_name, query in QUERIES.items():
        results[query_name] = pd.read_sql_query(query, connection)

    return results

def format_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Format column names for presentation in the HTML report."""
    formatted_df = df.copy()
    formatted_df.columns = [
        column.replace("_", " ").title()
        for column in formatted_df.columns
    ]
    return formatted_df

def dataframe_to_html_table(df: pd.DataFrame) -> str:
    """Convert a DataFrame to an HTML table with presentation-friendly column names."""
    formatted_df = format_column_names(df)

    return formatted_df.to_html(
        index=False,
        border=0,
        classes="data-table",
        justify="center",
    )


def build_kpi_cards(
    basic_kpis: pd.DataFrame,
    suspicious_kpis: pd.DataFrame,
) -> str:
    """Build HTML KPI cards from selected KPI query outputs."""
    basic = basic_kpis.iloc[0]
    suspicious = suspicious_kpis.iloc[0]

    cards = [
        ("Transactions", f"{int(basic['transaction_count']):,}"),
        ("Total amount", f"{basic['total_transaction_amount']:,.2f}"),
        ("Average amount", f"{basic['average_transaction_amount']:,.2f}"),
        ("Suspicious transactions", f"{int(suspicious['suspicious_transaction_count']):,}"),
        ("Suspicious rate", f"{suspicious['suspicious_transaction_rate_pct']:.2f}%"),
        ("Suspicious amount", f"{suspicious['suspicious_transaction_amount']:,.2f}"),
        ("Average risk score", f"{basic['average_risk_score']:.2f}"),
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
        <h2>Executive summary</h2>
        <div class="kpi-grid">
            {cards_html}
        </div>
    </section>
    """


def build_html_report(results: dict[str, pd.DataFrame]) -> str:
    """Build the full HTML report."""
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sections_html = ""

    for query_name, df in results.items():
        if query_name in ["basic_kpis", "suspicious_kpis"]:
            continue

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

    kpi_cards = build_kpi_cards(
        basic_kpis=results["basic_kpis"],
        suspicious_kpis=results["suspicious_kpis"],
    )

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transaction Monitoring Report</title>
<style>
    * {{
        box-sizing: border-box;
    }}

    body {{
        font-family: Arial, sans-serif;
        margin: 40px;
        color: #222;
        background-color: #fafafa;
        line-height: 1.5;
    }}

    h1 {{
        margin-bottom: 0;
        font-size: 32px;
    }}

    h2 {{
        font-size: 22px;
        margin-top: 0;
    }}

    .subtitle {{
        color: #666;
        margin-top: 5px;
        margin-bottom: 30px;
    }}

    section {{
        margin-top: 35px;
        padding: 20px;
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 8px;
    }}

    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 15px;
    }}

    .kpi-card {{
        padding: 16px;
        background-color: #f5f5f5;
        border-radius: 8px;
        border: 1px solid #ddd;
    }}

    .kpi-label {{
        font-size: 13px;
        color: #666;
        margin-bottom: 8px;
    }}

    .kpi-value {{
        font-size: 24px;
        font-weight: bold;
        overflow-wrap: anywhere;
    }}

    .table-wrapper {{
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }}

    .data-table {{
        width: 100%;
        min-width: 760px;
        border-collapse: collapse;
        margin-top: 10px;
        font-size: 14px;
    }}

    .data-table th {{
        background-color: #f0f0f0;
        text-align: left;
        padding: 8px;
        border-bottom: 2px solid #ccc;
        white-space: nowrap;
    }}

    .data-table td {{
        padding: 8px;
        border-bottom: 1px solid #ddd;
        white-space: nowrap;
    }}

    .note {{
        margin-top: 30px;
        font-size: 13px;
        color: #666;
    }}

    @media (max-width: 768px) {{
        body {{
            margin: 12px;
            font-size: 14px;
        }}

        h1 {{
            font-size: 24px;
            line-height: 1.2;
        }}

        h2 {{
            font-size: 18px;
        }}

        section {{
            margin-top: 18px;
            padding: 14px;
            border-radius: 6px;
        }}

        .subtitle {{
            margin-bottom: 18px;
            font-size: 13px;
        }}

        .kpi-grid {{
            grid-template-columns: 1fr;
            gap: 10px;
        }}

        .kpi-card {{
            padding: 12px;
        }}

        .kpi-value {{
            font-size: 20px;
        }}

        .data-table {{
            min-width: 720px;
            font-size: 12px;
        }}

        .data-table th,
        .data-table td {{
            padding: 6px;
        }}
    }}
</style>

</head>
<body>
    <h1>Bank Transaction Monitoring Report</h1>
    <p class="subtitle">
        Automated HTML report generated from the Kimball dimensional model.
        Generated at: {generated_at}
    </p>

    {kpi_cards}

    {sections_html}

    <p class="note">
        Note: The dataset does not include confirmed fraud labels. The anomaly flag
        identifies potentially suspicious transactions based on a rule-based scoring
        approach and should not be interpreted as confirmed fraud.
    </p>
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
            "Run scripts/04_build_dimensional_model.py first."
        )

    with sqlite3.connect(WAREHOUSE_PATH) as connection:
        results = run_queries(connection)

    html = build_html_report(results)
    save_report(html)


if __name__ == "__main__":
    main()
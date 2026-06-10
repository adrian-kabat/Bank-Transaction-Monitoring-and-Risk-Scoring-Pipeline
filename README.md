# Bank Transaction Monitoring and Anomaly Detection Pipeline

## Project overview

This project demonstrates an end-to-end analytics pipeline for bank transaction monitoring. Since the dataset does not include confirmed fraud labels, the project does not implement supervised fraud classification. Instead, it uses a rule-based risk scoring approach to identify potentially suspicious transactions that may require further review.

The project includes programmatic data ingestion, data cleaning, feature engineering, risk scoring, a Kimball dimensional model, SQL KPI queries, an automated HTML report, a FastAPI mock banking API, and a Power BI dashboard.

## Key features

* Programmatic data ingestion from KaggleHub.
* Data cleaning and feature engineering pipeline in Python.
* Rule-based transaction risk scoring.
* Kimball dimensional model with fact and dimension tables.
* SQLite analytical warehouse.
* SQL KPI queries for transaction monitoring.
* Automated responsive HTML report.
* Power BI dashboard with three analytical pages.
* FastAPI mock banking API.
* One-command pipeline orchestration.

## Tech stack

* Python
* pandas
* KaggleHub
* SQLite
* SQL
* FastAPI
* Uvicorn
* Power BI
* Git/GitHub

## Data source

The project uses the **Bank Transaction Dataset for Fraud Detection** from Kaggle:

```text
valakhorasani/bank-transaction-dataset-for-fraud-detection
```

The data is downloaded programmatically using KaggleHub. Raw data files are excluded from version control.

## Modeling approach

The dataset does not contain a confirmed fraud label. Therefore, the project does not classify transactions as confirmed fraud or non-fraud.

Instead, the project focuses on transaction monitoring and rule-based anomaly detection. The generated `suspicious_flag` should be interpreted as a signal for potentially suspicious transactions, not as a confirmed fraud label.

The risk scoring logic is intentionally separated from the data cleaning pipeline to make future development easier.

## Pipeline

```text
KaggleHub
    ↓
Raw data
    ↓
Data cleaning and feature engineering
    ↓
Rule-based risk scoring
    ↓
Kimball dimensional model
    ↓
SQLite analytical warehouse
    ↓
SQL KPI queries
    ↓
Automated HTML report
    ↓
CSV export for Power BI
    ↓
Power BI dashboard
```

The FastAPI mock API is implemented as a separate module and can be used to simulate ingestion from a banking source system.

## Repository structure

```text
financial-fraud-analytics-pipeline/
├── app/
│   ├── main.py
│   └── services/
│       ├── __init__.py
│       └── data_service.py
├── data/
│   ├── api/
│   ├── model/
│   ├── processed/
│   └── raw/
├── docs/
│   ├── dashboard_screenshots/
│   ├── kimball_dimensional_model.md
│   └── risk_scoring_method.md
├── powerbi/
│   └── transaction_monitoring_dashboard.pbix
├── reports/
├── scripts/
│   ├── 00_download_data.py
│   ├── 01_inspect_data.py
│   ├── 02_profile_data.py
│   ├── 03_clean_transactions.py
│   ├── 04_score_transactions.py
│   ├── 05_build_dimensional_model.py
│   ├── 06_test_kpi_queries.py
│   ├── 07_generate_html_report.py
│   ├── 08_export_model_tables.py
│   ├── 09_fetch_from_api.py
│   └── 10_run_pipeline.py
├── sql/
│   └── 01_kpi_queries.sql
├── warehouse/
├── .gitignore
├── README.md
└── requirements.txt
```

## How to run

### 1. Clone the repository

```bash
git clone <repository-url>
cd financial-fraud-analytics-pipeline
```

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the full analytical pipeline

```bash
python scripts/10_run_pipeline.py
```

This command executes the main analytical workflow:

1. downloads raw data from KaggleHub,
2. inspects and profiles raw data,
3. cleans transaction data,
4. applies rule-based risk scoring,
5. builds the Kimball dimensional model,
6. tests SQL KPI queries,
7. generates the automated HTML report,
8. exports model tables for Power BI.

### 5. Open generated outputs

After the pipeline completes, the main generated files are:

```text
data/processed/transactions_clean.csv
data/processed/transactions_scored.csv
warehouse/transaction_monitoring.db
reports/transaction_monitoring_report.html
data/model/*.csv
```

Generated data files, warehouse files, and HTML reports are excluded from version control.

## Mock banking API

The project includes a FastAPI-based mock banking API that exposes cleaned and risk-scored transaction data. The API simulates a banking source system used by the analytical pipeline.

### Available endpoints

* `GET /health`
* `GET /summary`
* `GET /transactions`
* `GET /accounts`
* `GET /merchants`
* `GET /channels`

### Run the API locally

The API is run separately because it is a long-running local service.

```bash
uvicorn app.main:app --reload
```

After starting the API, the interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### Test the API

To check whether the API is running correctly, open:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

You can also open the summary endpoint:

```text
http://127.0.0.1:8000/summary
```

The root URL may return `404 Not Found` if no `/` endpoint is defined. Use `/docs`, `/health`, or the listed endpoints to test the API.

### Fetch data from the API

With the API running, execute the following command in a second terminal:

```bash
python scripts/09_fetch_from_api.py
```

The API response will be saved locally to:

```text
data/api/transactions_from_api.csv
```

Raw API output files are excluded from version control.

## Kimball dimensional model

The analytical layer follows the Kimball dimensional modeling approach. Transaction-level events are stored in the central fact table, while descriptive business context is separated into dimension tables.

### Fact table

```text
fact_transactions
```

The grain of the fact table is one row per bank transaction.

Main measures and indicators:

* `transaction_amount`
* `transaction_duration`
* `login_attempts`
* `account_balance`
* `minutes_since_previous_transaction`
* `transaction_count`
* `risk_score`
* `suspicious_flag`

### Dimension tables

```text
dim_account
dim_date
dim_merchant
dim_channel
dim_location
dim_device
dim_transaction_type
```

All relationships follow a one-to-many structure from dimension tables to the fact table.

Detailed documentation is available in:

```text
docs/kimball_dimensional_model.md
```

## Risk scoring method

The project uses a transparent rule-based risk scoring method. The current score is heuristic and should be interpreted as a transaction monitoring signal.

Generated variables:

| Variable          | Description                                                 |
| ----------------- | ----------------------------------------------------------- |
| `risk_score`      | Numeric risk score calculated from rule-based indicators    |
| `suspicious_flag` | Binary flag identifying potentially suspicious transactions |
| `risk_level`      | Categorical risk level: Low, Medium, High                   |

Detailed documentation is available in:

```text
docs/risk_scoring_method.md
```

## SQL KPI queries

SQL queries are stored in:

```text
sql/01_kpi_queries.sql
```

The queries cover:

* transaction volume,
* transaction value,
* suspicious transaction count,
* suspicious transaction rate,
* risk by channel,
* risk by transaction type,
* risk by location,
* risk by hour,
* top high-risk transactions.

## Automated HTML report

The automated report is generated by:

```bash
python scripts/07_generate_html_report.py
```

The generated report is saved to:

```text
reports/transaction_monitoring_report.html
```

The report includes:

* executive KPI summary,
* risk level distribution,
* risk by channel,
* risk by transaction type,
* risk by location,
* high-risk transaction review table,
* risk by hour of day.

## Power BI dashboard

The Power BI dashboard contains three analytical pages:

1. **Executive Risk Overview**
   High-level summary of transaction volume, suspicious activity, and risk exposure.

2. **Risk Drivers**
   Analysis of risk indicators across channels, transaction types, locations, and time patterns.

3. **Operational Monitoring**
   Operational view of high-risk segments and transactions requiring further review.

The Power BI file is stored in:

```text
powerbi/transaction_monitoring_dashboard.pbix
```

Dashboard screenshots can be stored in:

```text
docs/dashboard_screenshots/
```

## Project outputs

The project generates the following local artifacts:

| Output             | Path                                            | Description                                      |
| ------------------ | ----------------------------------------------- | ------------------------------------------------ |
| Clean dataset      | `data/processed/transactions_clean.csv`         | Cleaned transaction data                         |
| Scored dataset     | `data/processed/transactions_scored.csv`        | Transactions with risk score and suspicious flag |
| SQLite warehouse   | `warehouse/transaction_monitoring.db`           | Local analytical warehouse                       |
| HTML report        | `reports/transaction_monitoring_report.html`    | Automated KPI report                             |
| Power BI exports   | `data/model/*.csv`                              | Model tables exported for Power BI               |
| API output         | `data/api/transactions_from_api.csv`            | Data fetched from the mock API                   |
| Power BI dashboard | `powerbi/transaction_monitoring_dashboard.pbix` | Interactive Power BI dashboard                   |

## Version control notes

The repository excludes generated and local files such as:

* raw data files,
* processed data files,
* exported model CSV files,
* SQLite warehouse files,
* generated HTML reports,
* API output files,
* virtual environments,
* local IDE settings.

This keeps the repository lightweight and reproducible.

## Limitations

The dataset does not include confirmed fraud labels. Therefore, the project does not implement supervised fraud classification.

The generated `suspicious_flag` is a transaction monitoring signal and should not be interpreted as confirmed fraud. The current `risk_score` is based on a heuristic rule-based approach and is intended for analytical and portfolio purposes.

## Future improvements

Potential extensions include:

* configurable risk scoring rules,
* moving scoring thresholds to a YAML or JSON configuration file,
* adding risk reason codes,
* comparing rule-based scoring with unsupervised anomaly detection,
* adding an Isolation Forest model,
* adding Docker support,
* adding automated tests,
* adding a Streamlit dashboard,
* publishing the API or report through a lightweight cloud deployment.

## Portfolio summary

This project demonstrates the ability to design and implement an end-to-end analytics workflow, including data ingestion, data preparation, dimensional modeling, SQL analytics, report automation, API development, and Power BI dashboarding.

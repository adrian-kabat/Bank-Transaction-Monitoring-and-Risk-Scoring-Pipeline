# Bank Transaction Monitoring and Anomaly Detection Pipeline

## Project overview

This project demonstrates an end-to-end analytics pipeline for bank transaction monitoring. Since the dataset does not include confirmed fraud labels, the project uses a rule-based risk scoring approach to identify potentially suspicious transactions.

The pipeline includes KaggleHub data ingestion, data cleaning, risk scoring, a Kimball dimensional model, SQL KPI queries, automated HTML reporting, and a Power BI dashboard.

## Tech stack

- Python
- pandas
- KaggleHub
- SQLite
- SQL
- Power BI
- Git/GitHub

## Pipeline

```text
KaggleHub
    ↓
Raw data
    ↓
Data cleaning
    ↓
Risk scoring
    ↓
Kimball dimensional model
    ↓
SQLite warehouse
    ↓
CSV export for Power BI
    ↓
SQL KPI queries
    ↓
Automated HTML report
    ↓
Power BI dashboard
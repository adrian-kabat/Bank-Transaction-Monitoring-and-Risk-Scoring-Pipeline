# Business assumptions

## Purpose

This document describes the main business assumptions behind the bank transaction monitoring pipeline.

The project simulates an analytical workflow for identifying transactions that may require further review. It does not attempt to confirm fraud. Instead, it focuses on transaction monitoring, risk prioritization, KPI reporting, and operational review support.

## Business context

Financial institutions often need to monitor large volumes of transactions and identify cases that may require further investigation. In real-world environments, confirmed fraud labels may be unavailable, delayed, incomplete, or inconsistent across systems.

Because of that, transaction monitoring systems often rely on a combination of:

* transparent business rules,
* risk indicators,
* analyst review queues,
* statistical anomaly detection,
* periodic KPI reporting.

This project reflects that scenario by combining rule-based risk scoring with an unsupervised anomaly detection comparison.

## Main business objective

The main objective is to support analysts in prioritizing transactions for further review.

The pipeline is designed to answer questions such as:

* Which transactions appear potentially suspicious?
* Which transactions have the highest risk scores?
* Why was a transaction assigned a high risk score?
* Which channels, transaction types, locations, or hours show higher risk exposure?
* How do rule-based monitoring results compare with unsupervised anomaly detection results?
* How can transaction monitoring KPIs be reported in a repeatable way?

## Key monitoring assumptions

The project assumes that a transaction may require further review when it shows one or more risk-related patterns, such as:

* unusually high transaction amount,
* very high transaction amount relative to the dataset,
* multiple login attempts,
* unusually long transaction duration,
* low account balance,
* transaction during night hours,
* very short time since the previous transaction.

These patterns are implemented as transparent rule-based indicators and stored as interpretable `risk_reasons`.

## Risk prioritization logic

The project uses a heuristic risk scoring approach.

Each transaction receives:

* `risk_score`,
* `suspicious_flag`,
* `risk_level`,
* `risk_reasons`.

The score is not a fraud probability. It is a monitoring signal that helps prioritize transactions for further review.

The risk score is designed to be:

* transparent,
* easy to explain,
* configurable,
* suitable for reporting,
* suitable for operational review queues.

## Reason codes

Reason codes are used to explain why a transaction received risk points.

Examples include:

* `high_amount_p95`,
* `very_high_amount_p99`,
* `multiple_login_attempts`,
* `long_transaction_duration`,
* `low_account_balance`,
* `night_transaction`,
* `short_interval_since_previous_transaction`.

This makes the output more interpretable than a numerical score alone.

## Analytical outputs

The project produces analytical outputs for several user groups:

| User group         | Example need                    | Project output                                |
| ------------------ | ------------------------------- | --------------------------------------------- |
| Analyst            | Review high-risk transactions   | High-risk transaction table with reason codes |
| BI user            | Monitor risk KPIs               | Power BI dashboard and HTML report            |
| Data engineer      | Maintain reproducible data flow | Python pipeline and SQLite warehouse          |
| Technical reviewer | Validate project quality        | pytest tests and GitHub Actions               |
| Developer          | Access data through an API      | FastAPI mock banking API                      |

## Reporting assumptions

The reporting layer focuses on transaction monitoring KPIs, including:

* total transaction count,
* total transaction amount,
* suspicious transaction count,
* suspicious transaction rate,
* average risk score,
* risk by channel,
* risk by transaction type,
* risk by location,
* risk by hour,
* high-risk transaction review queue.

These metrics are intended to support monitoring and prioritization, not final fraud adjudication.

## Data modeling assumptions

The project uses a Kimball-style dimensional model because transaction monitoring requires repeatable analysis across multiple descriptive dimensions.

The fact table stores transaction-level events, while dimension tables describe business context such as:

* account,
* date,
* merchant,
* channel,
* location,
* device,
* transaction type.

This structure supports SQL KPI queries and Power BI reporting.

## Important interpretation note

The project does not determine whether a transaction is fraudulent.

A transaction marked as suspicious should be interpreted as:

> This transaction shows risk-related patterns and may require further review.

It should not be interpreted as:

> This transaction is confirmed fraud.

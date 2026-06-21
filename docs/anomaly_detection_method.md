# Anomaly detection method

## Purpose

This document describes the unsupervised anomaly detection component used in the project.

The anomaly detection module is added as a comparison layer to the transparent rule-based risk scoring system. It does not replace the rule-based approach and does not confirm fraud.

## Why unsupervised anomaly detection?

The dataset does not contain confirmed fraud labels. Therefore, supervised fraud classification is not appropriate.

Unsupervised anomaly detection is more suitable in this context because it can identify transactions that are unusual relative to the rest of the dataset without requiring a confirmed target label.

The project uses anomaly detection to compare two monitoring approaches:

| Approach                | Description                                                                             |
| ----------------------- | --------------------------------------------------------------------------------------- |
| Rule-based risk scoring | Transparent, configurable business logic based on explicit risk indicators.             |
| Isolation Forest        | Unsupervised machine learning model for identifying statistically unusual transactions. |

## Model choice

The project uses Isolation Forest.

Isolation Forest is suitable for this portfolio project because:

* it works without confirmed fraud labels,
* it is commonly used for anomaly detection,
* it can handle multiple numerical features,
* it provides an anomaly decision output,
* it is simple enough to explain in a portfolio context.

## Input data

The anomaly detection model uses the risk-scored transaction dataset:

```text
data/processed/transactions_scored.csv
```

The output is saved to:

```text
data/processed/transactions_with_anomaly_model.csv
```

A comparison summary is saved to:

```text
reports/anomaly_model_comparison.csv
```

## Features used

The model uses selected numerical transaction features:

| Feature                              | Rationale                                            |
| ------------------------------------ | ---------------------------------------------------- |
| `transaction_amount`                 | Captures transaction size.                           |
| `transaction_duration`               | Captures unusually long transaction processing time. |
| `login_attempts`                     | Captures potentially suspicious login behavior.      |
| `account_balance`                    | Captures account-level financial context.            |
| `minutes_since_previous_transaction` | Captures short intervals between transactions.       |
| `transaction_hour`                   | Captures time-of-day behavior.                       |

The selected features are configured in:

```text
config/anomaly_model.yaml
```

## Configuration

The model configuration is stored outside the Python code.

Example:

```yaml
model:
  name: isolation_forest
  contamination: 0.05
  random_state: 42
  n_estimators: 200

features:
  - transaction_amount
  - transaction_duration
  - login_attempts
  - account_balance
  - minutes_since_previous_transaction
  - transaction_hour
```

This makes the model settings easier to review and adjust.

## Preprocessing

Before fitting the model:

1. selected features are extracted from the scored transaction dataset,
2. values are converted to numeric format,
3. missing values are imputed with median values,
4. features are standardized using `StandardScaler`.

Standardization helps place numerical variables on a comparable scale before applying the Isolation Forest model.

## Model outputs

The anomaly detection script produces three main fields:

| Output                      | Description                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------- |
| `ml_anomaly_decision_score` | Raw Isolation Forest decision score. Lower values indicate more unusual observations.         |
| `ml_anomaly_score`          | Normalized anomaly score from 0 to 100, where higher values indicate stronger anomaly signal. |
| `ml_anomaly_flag`           | Binary flag indicating whether the model identified the transaction as an anomaly.            |

## Comparison with rule-based scoring

The project compares the Isolation Forest output with the rule-based `suspicious_flag`.

The comparison report contains:

| Metric                               | Description                                                |
| ------------------------------------ | ---------------------------------------------------------- |
| `total_transactions`                 | Total number of transactions.                              |
| `rule_based_suspicious_transactions` | Number of transactions flagged by rule-based scoring.      |
| `ml_anomaly_transactions`            | Number of transactions flagged by Isolation Forest.        |
| `flagged_by_both_methods`            | Number of transactions flagged by both approaches.         |
| `rule_based_only`                    | Number of transactions flagged only by rule-based scoring. |
| `ml_only`                            | Number of transactions flagged only by the ML model.       |

This comparison helps show whether business rules and statistical anomaly detection identify similar or different transaction patterns.

## Interpretation

The Isolation Forest output should be interpreted as an anomaly signal, not as confirmed fraud.

A transaction flagged by the model means:

> The transaction appears statistically unusual compared with other transactions in the dataset.

It does not mean:

> The transaction is confirmed fraud.

## Why both approaches are useful

Rule-based scoring is useful because it is transparent and easy to explain. Analysts can see exactly which reason codes contributed to a transaction’s risk score.

Isolation Forest is useful because it may detect unusual combinations of features that are not directly captured by explicit business rules.

Together, they demonstrate two complementary approaches to transaction monitoring:

* interpretable business rules,
* unsupervised statistical anomaly detection.

## Limitations

The anomaly detection model is limited by:

* lack of confirmed fraud labels,
* limited feature set,
* local batch-processing context,
* no production model monitoring,
* no validation against confirmed investigation outcomes.

Because of these limitations, the model is included as an analytical comparison layer rather than a production fraud detection model.

# Risk Scoring Method

## Overview

The project uses a rule-based risk scoring method to identify potentially suspicious transactions. The dataset does not contain confirmed fraud labels, so the scoring output should not be interpreted as confirmed fraud detection.

The current approach is intentionally simple, transparent, and explainable. It can be extended in future versions with configurable thresholds, weighted scoring, or unsupervised anomaly detection models.

## Current rules

| Risk indicator | Points |
|---|---:|
| Transaction amount greater than or equal to the 95th percentile | +30 |
| Transaction amount greater than or equal to the 99th percentile | +20 |
| More than one login attempt | +20 |
| Transaction duration greater than or equal to the 95th percentile | +20 |
| Account balance lower than or equal to the 5th percentile | +20 |
| Transaction between 00:00 and 05:59 | +10 |
| Time since previous transaction lower than or equal to 10 minutes | +20 |

## Output variables

| Variable | Description |
|---|---|
| `risk_score` | Numeric risk score calculated from rule-based indicators |
| `suspicious_flag` | Binary flag identifying potentially suspicious transactions |
| `risk_level` | Categorical risk level: Low, Medium, High |

## Interpretation

The `suspicious_flag` indicates transactions that should be reviewed further. It is not equivalent to a confirmed fraud label.

## Future improvements

Potential extensions:

- configurable risk thresholds,
- separation of scoring rules into a YAML or JSON configuration file,
- model comparison between rule-based scoring and Isolation Forest,
- adding risk reason codes,
- monitoring risk score distribution over time.
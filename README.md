## Project overview

This project demonstrates an end-to-end analytics pipeline for bank transaction monitoring. Since the dataset does not include confirmed fraud labels, the project uses a rule-based anomaly scoring approach to identify potentially suspicious transactions.

The pipeline includes KaggleHub data ingestion, Python-based data preparation, anomaly scoring, dimensional modeling, SQL KPI queries, automated reporting, and a Power BI dashboard.

## Risk scoring approach

The project currently uses a rule-based anomaly scoring method. This approach is intentionally separated from the data cleaning pipeline to make the risk model easier to maintain and extend.

The current `anomaly_score` is heuristic and should be interpreted as a suspicious transaction indicator, not as a confirmed fraud prediction.

Future versions may include:
- weighted risk scoring,
- configurable thresholds,
- unsupervised anomaly detection,
- Isolation Forest,
- model monitoring,
- comparison of rule-based and ML-based approaches.

## Model wymiarowy Kimballa

Warstwa analityczna projektu została zaprojektowana zgodnie z podejściem Kimballa do modelowania wymiarowego. Zdarzenia transakcyjne są przechowywane w centralnej tabeli faktów, natomiast kontekst opisowy znajduje się w tabelach wymiarów.

Model wspiera raportowanie, analizę KPI, monitorowanie anomalii oraz budowę dashboardu w Power BI.
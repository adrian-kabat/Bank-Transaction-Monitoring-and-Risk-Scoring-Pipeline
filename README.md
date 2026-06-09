## Project overview

This project demonstrates an end-to-end analytics pipeline for bank transaction monitoring. Since the dataset does not include confirmed fraud labels, the project uses a rule-based anomaly scoring approach to identify potentially suspicious transactions.

The pipeline includes KaggleHub data ingestion, Python-based data preparation, anomaly scoring, dimensional modeling, SQL KPI queries, automated reporting, and a Power BI dashboard.

## Modeling approach

The dataset does not contain a confirmed fraud label. Therefore, this project does not implement supervised fraud classification.

Instead, it focuses on transaction monitoring and rule-based anomaly detection. The generated `anomaly_flag` should be interpreted as an indicator of potentially suspicious transactions requiring further review, not as confirmed fraud.

## Model wymiarowy Kimballa

Warstwa analityczna projektu została zaprojektowana zgodnie z podejściem Kimballa do modelowania wymiarowego. Zdarzenia transakcyjne są przechowywane w centralnej tabeli faktów, natomiast kontekst opisowy znajduje się w tabelach wymiarów.

Model wspiera raportowanie, analizę KPI, monitorowanie anomalii oraz budowę dashboardu w Power BI.
# Limitations

## Purpose

This document describes the main limitations of the project and clarifies how the outputs should be interpreted.

The project is designed as a portfolio project demonstrating an end-to-end analytics and reporting pipeline for bank transaction monitoring. It should not be interpreted as a production fraud detection system.

## No confirmed fraud labels

The dataset does not include confirmed fraud labels.

Because of that, the project does not implement supervised fraud classification. There is no target variable that would allow the model to learn confirmed fraud and non-fraud examples.

As a result:

* `suspicious_flag` is not a confirmed fraud label,
* `risk_score` is not a fraud probability,
* `ml_anomaly_flag` is not a confirmed fraud prediction,
* model evaluation using precision, recall, F1-score, ROC-AUC, or confusion matrix is not possible in the classical supervised sense.

## Rule-based scoring is heuristic

The rule-based scoring logic is based on transparent heuristic indicators.

The rules are useful for monitoring and prioritization, but they are not statistically validated against confirmed fraud outcomes.

The scoring logic should be interpreted as a configurable analytical layer, not as a certified decision model.

## Isolation Forest does not confirm fraud

The Isolation Forest module identifies statistically unusual transactions based on selected numerical features.

An unusual transaction is not necessarily fraudulent. It may be unusual because of legitimate customer behavior, transaction context, dataset structure, or feature distribution.

The Isolation Forest output is therefore used only as a comparison layer against rule-based scoring.

## No production-grade fraud investigation workflow

The project does not include a full fraud investigation lifecycle.

It does not cover:

* case management,
* analyst decisions,
* false positive review,
* customer contact,
* regulatory reporting,
* alert escalation,
* feedback loops from confirmed cases,
* model retraining based on investigation outcomes.

## Limited feature set

The project uses the variables available in the dataset.

The dataset does not include many features that would typically be useful in a real transaction monitoring system, such as:

* customer transaction history over long time windows,
* merchant risk category,
* country-level risk indicators,
* device reputation,
* IP geolocation risk,
* customer segment,
* card-present vs card-not-present context,
* historical fraud outcomes,
* confirmed chargebacks,
* analyst review outcomes.

## No temporal production environment

The project runs as a local batch pipeline.

It does not implement:

* real-time streaming,
* message queues,
* incremental loading,
* scheduled orchestration,
* production monitoring,
* alert delivery,
* data lineage tracking,
* role-based access control.

## Local analytical warehouse

The project uses SQLite as a lightweight local analytical warehouse.

SQLite is suitable for portfolio demonstration, local development, and reproducible examples. It is not intended here as a replacement for production data warehouse technologies.

In a production environment, this layer could be implemented in tools such as PostgreSQL, Snowflake, BigQuery, Redshift, Azure Synapse, or another analytical platform.

## No deployment security layer

The FastAPI application is a mock banking API for local demonstration.

It does not include:

* authentication,
* authorization,
* rate limiting,
* input validation for all production scenarios,
* audit logging,
* encryption configuration,
* secrets management,
* production deployment hardening.

## Dashboard limitations

The Power BI dashboard is designed for portfolio demonstration and analytical presentation.

It does not include:

* row-level security,
* scheduled refresh,
* production gateway setup,
* shared workspace deployment,
* role-specific dashboards,
* formal stakeholder acceptance testing.

## Interpretation of project outputs

The project outputs should be interpreted as transaction monitoring support tools.

They are useful for:

* prioritizing review,
* understanding risk patterns,
* generating KPIs,
* demonstrating data engineering and analytics workflow design.

They are not sufficient for:

* confirming fraud,
* making automated adverse decisions,
* replacing analyst review,
* meeting regulatory fraud detection requirements.

## Summary

The main limitation is the absence of confirmed fraud labels. The project addresses this responsibly by using transparent rule-based scoring and unsupervised anomaly detection as monitoring signals rather than pretending to perform confirmed fraud classification.

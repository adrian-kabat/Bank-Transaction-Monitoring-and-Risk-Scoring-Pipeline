from pathlib import Path

import pandas as pd
import yaml
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "transactions_scored.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "transactions_with_anomaly_model.csv"
COMPARISON_OUTPUT_PATH = PROJECT_ROOT / "reports" / "anomaly_model_comparison.csv"
CONFIG_PATH = PROJECT_ROOT / "config" / "anomaly_model.yaml"


def load_config() -> dict:
    """Load anomaly detection model configuration."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_scored_transactions() -> pd.DataFrame:
    """Load transactions with rule-based risk scoring."""
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}. "
            "Run scripts/04_score_transactions.py first."
        )

    return pd.read_csv(INPUT_PATH)


def prepare_features(df: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    """Prepare numerical features for anomaly detection."""
    missing_columns = set(feature_columns) - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing feature columns: {missing_columns}")

    features = df[feature_columns].copy()

    for column in feature_columns:
        features[column] = pd.to_numeric(features[column], errors="coerce")

    features = features.fillna(features.median(numeric_only=True))

    return features


def add_isolation_forest_scores(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Add unsupervised anomaly detection scores using Isolation Forest."""
    df = df.copy()

    feature_columns = config["features"]
    model_config = config["model"]

    features = prepare_features(df, feature_columns)

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    model = IsolationForest(
        n_estimators=model_config["n_estimators"],
        contamination=model_config["contamination"],
        random_state=model_config["random_state"],
    )

    model.fit(scaled_features)

    decision_scores = model.decision_function(scaled_features)
    predictions = model.predict(scaled_features)

    df["ml_anomaly_decision_score"] = decision_scores
    df["ml_anomaly_flag"] = (predictions == -1).astype(int)

    min_score = decision_scores.min()
    max_score = decision_scores.max()

    if max_score == min_score:
        df["ml_anomaly_score"] = 0
    else:
        df["ml_anomaly_score"] = (
            100
            * (max_score - decision_scores)
            / (max_score - min_score)
        ).round(2)

    return df


def create_comparison_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compare rule-based suspicious flags with ML anomaly flags."""
    summary = pd.DataFrame(
        {
            "metric": [
                "total_transactions",
                "rule_based_suspicious_transactions",
                "ml_anomaly_transactions",
                "flagged_by_both_methods",
                "rule_based_only",
                "ml_only",
            ],
            "value": [
                len(df),
                int(df["suspicious_flag"].sum()),
                int(df["ml_anomaly_flag"].sum()),
                int(((df["suspicious_flag"] == 1) & (df["ml_anomaly_flag"] == 1)).sum()),
                int(((df["suspicious_flag"] == 1) & (df["ml_anomaly_flag"] == 0)).sum()),
                int(((df["suspicious_flag"] == 0) & (df["ml_anomaly_flag"] == 1)).sum()),
            ],
        }
    )

    return summary


def save_outputs(df: pd.DataFrame, comparison_summary: pd.DataFrame) -> None:
    """Save enriched transactions and comparison summary."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    COMPARISON_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_PATH, index=False)
    comparison_summary.to_csv(COMPARISON_OUTPUT_PATH, index=False)

    print(f"Transactions with anomaly model saved to: {OUTPUT_PATH}")
    print(f"Comparison summary saved to: {COMPARISON_OUTPUT_PATH}")

    print("\nComparison summary:")
    print(comparison_summary.to_string(index=False))


def main() -> None:
    config = load_config()
    df = load_scored_transactions()
    df = add_isolation_forest_scores(df, config)
    comparison_summary = create_comparison_summary(df)
    save_outputs(df, comparison_summary)


if __name__ == "__main__":
    main()
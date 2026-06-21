from pathlib import Path
import subprocess
import sys
from time import perf_counter


PROJECT_ROOT = Path(__file__).resolve().parents[1]


PIPELINE_STEPS = [
    {
        "name": "Download raw data from KaggleHub",
        "script": "00_download_data.py",
        "required": True,
    },
    {
        "name": "Inspect raw data",
        "script": "01_inspect_data.py",
        "required": False,
    },
    {
        "name": "Profile raw data",
        "script": "02_profile_data.py",
        "required": False,
    },
    {
        "name": "Clean transaction data",
        "script": "03_clean_transactions.py",
        "required": True,
    },
    {
        "name": "Apply risk scoring",
        "script": "04_score_transactions.py",
        "required": True,
    },

    {
        "name": "Train anomaly model ",
        "script": "11_train_anomaly_model.py",
        "required": True,
    },

    {
        "name": "Build Kimball dimensional model",
        "script": "05_Kimball_dimensional_model.py",
        "required": True,
    },
    {
        "name": "Test SQL KPI queries",
        "script": "06_test_kpi_queries.py",
        "required": True,
    },
    {
        "name": "Generate automated HTML report",
        "script": "07_generate_html_report.py",
        "required": True,
    },
    {
        "name": "Export model tables for Power BI",
        "script": "08_export_model_tables.py",
        "required": True,
    },
]


def run_step(step: dict) -> None:
    """Run a single pipeline step as a Python subprocess."""
    script_path = PROJECT_ROOT / "scripts" / step["script"]

    if not script_path.exists():
        message = f"Script not found: {script_path}"

        if step["required"]:
            raise FileNotFoundError(message)

        print(f"Skipping optional step. {message}")
        return

    print("\n" + "=" * 80)
    print(f"Running step: {step['name']}")
    print(f"Script: {step['script']}")
    print("=" * 80)

    start_time = perf_counter()

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        check=False,
    )

    elapsed_time = perf_counter() - start_time

    if result.returncode != 0:
        raise RuntimeError(
            f"Pipeline step failed: {step['name']} "
            f"({step['script']})"
        )

    print(f"Completed step: {step['name']} in {elapsed_time:.2f} seconds")


def run_pipeline() -> None:
    """Run the full analytical pipeline."""
    pipeline_start_time = perf_counter()

    print("\nStarting transaction monitoring pipeline...")
    print(f"Project root: {PROJECT_ROOT}")

    for step in PIPELINE_STEPS:
        run_step(step)

    total_elapsed_time = perf_counter() - pipeline_start_time

    print("\n" + "=" * 80)
    print("Pipeline completed successfully.")
    print(f"Total runtime: {total_elapsed_time:.2f} seconds")
    print("=" * 80)


if __name__ == "__main__":
    run_pipeline()
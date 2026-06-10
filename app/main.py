from fastapi import FastAPI, Query

from app.services.data_service import (
    get_accounts,
    get_api_summary,
    get_channels,
    get_merchants,
    get_transactions,
)


app = FastAPI(
    title="Bank Transaction Monitoring API",
    description=(
        "Mock banking API for transaction monitoring and anomaly detection. "
        "The API exposes cleaned and risk-scored transaction data for ingestion "
        "into an analytical pipeline."
    ),
    version="1.0.0",
)


@app.get("/health")
def health_check() -> dict:
    """Check API status."""
    return {"status": "ok"}


@app.get("/summary")
def summary() -> dict:
    """Return high-level summary statistics."""
    return get_api_summary()


@app.get("/transactions")
def transactions(
    limit: int = Query(default=100, ge=1, le=1000),
    risk_level: str | None = Query(default=None),
    channel: str | None = Query(default=None),
) -> list[dict]:
    """Return transactions with optional filters."""
    return get_transactions(
        limit=limit,
        risk_level=risk_level,
        channel=channel,
    )


@app.get("/accounts")
def accounts() -> list[dict]:
    """Return unique accounts."""
    return get_accounts()


@app.get("/merchants")
def merchants() -> list[dict]:
    """Return unique merchants."""
    return get_merchants()


@app.get("/channels")
def channels() -> list[dict]:
    """Return unique channels."""
    return get_channels()
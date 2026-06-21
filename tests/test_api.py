from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_summary_endpoint_returns_expected_fields() -> None:
    response = client.get("/summary")

    assert response.status_code == 200

    data = response.json()

    expected_fields = {
        "transaction_count",
        "account_count",
        "merchant_count",
        "channel_count",
        "suspicious_transaction_count",
        "average_risk_score",
    }

    missing_fields = expected_fields - set(data.keys())

    assert not missing_fields, f"Missing summary fields: {missing_fields}"


def test_transactions_endpoint_returns_limited_list() -> None:
    response = client.get("/transactions?limit=5")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 5


def test_transactions_endpoint_returns_risk_fields() -> None:
    response = client.get("/transactions?limit=5")

    assert response.status_code == 200

    data = response.json()

    if data:
        first_transaction = data[0]

        expected_fields = {
            "risk_score",
            "suspicious_flag",
            "risk_level",
            "risk_reasons",
        }

        missing_fields = expected_fields - set(first_transaction.keys())

        assert not missing_fields, f"Missing transaction fields: {missing_fields}"


def test_accounts_endpoint_returns_list() -> None:
    response = client.get("/accounts")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_merchants_endpoint_returns_list() -> None:
    response = client.get("/merchants")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_channels_endpoint_returns_list() -> None:
    response = client.get("/channels")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
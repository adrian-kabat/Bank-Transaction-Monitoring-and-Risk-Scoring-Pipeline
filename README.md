## Pipeline

```text
KaggleHub
    ↓
Raw data
    ↓
Data cleaning
    ↓
Risk scoring
    ↓
Kimball dimensional model
    ↓
SQLite warehouse
    ↓
CSV export for Power BI
    ↓
SQL KPI queries
    ↓
Automated HTML report
    ↓
Power BI dashboard
```

## Mock banking API

The project includes a FastAPI-based mock banking API that exposes cleaned and risk-scored transaction data. The API simulates a banking source system used by the analytical pipeline.

### Available endpoints

- `GET /health`
- `GET /summary`
- `GET /transactions`
- `GET /accounts`
- `GET /merchants`
- `GET /channels`

### Run the API locally

```bash
uvicorn app.main:app --reload
```

After starting the API, the interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### Test the API

To check whether the API is running correctly, open:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

You can also open the summary endpoint:

```text
http://127.0.0.1:8000/summary
```

### Fetch data from the API

With the API running, execute the following command in a second terminal:

```bash
python scripts/09_fetch_from_api.py
```

The API response will be saved locally to:

```text
data/api/transactions_from_api.csv
```

Raw API output files are excluded from version control.

### Note

The root URL may return `404 Not Found` if no `/` endpoint is defined. Use `/docs`, `/health`, or the listed endpoints to test the API.
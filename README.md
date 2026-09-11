# crm-erp-sync-engine

FastAPI middleware that validates CRM order events, transforms them into an ERP contract, submits them asynchronously, and records the outcome for audit and operations.

## Flow

```text
CRM -> POST /api/v1/crm/order-created -> Pydantic validation
                                      -> ERP adapter with exponential retry
                                      -> sync_logs transaction
```

The request creates a `PENDING` audit record before the ERP call. A successful response marks it `SUCCESS`; exhausted transport or 5xx failures mark it `FAILED` and return `502`. Validation errors are rejected before the service layer. `sync_logs` uses SQLite by default for local execution and can use PostgreSQL through `DATABASE_URL`.

## Run locally

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
pytest
uvicorn app.main:app --reload
```

The API and OpenAPI UI are available at `http://localhost:8000/docs`.

## Docker

```bash
cp .env.example .env
docker compose up --build
```

The Compose ERP service is a local HTTP target for network wiring; replace `ERP_BASE_URL` with the real ERP endpoint in a deployed environment.

## Request example

```bash
curl -X POST http://localhost:8000/api/v1/crm/order-created \
  -H 'content-type: application/json' \
  -d '{
    "order_id": "crm-100",
    "lead": {"name": "Ada Lovelace", "email": "ada@example.com", "phone": "0044 20 1234 5678"},
    "items": [{"sku": "CPU-1", "name": "Processor", "quantity": 2, "unit_price": "50.00"}],
    "status": "confirmed",
    "total_price": "100.00",
    "currency": "GBP"
  }'
```

Supported source currencies are EUR, USD, and GBP; ERP output is normalized to EUR. Phone numbers are normalized to digits and an optional leading `+`. The calculated item total must match `total_price`.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | SQLite | Async SQLAlchemy database URL |
| `ERP_BASE_URL` | `http://erp:8080` | ERP adapter base URL |
| `ERP_API_TOKEN` | empty | Bearer token for ERP |
| `ERP_TIMEOUT_SECONDS` | `10` | Request timeout |
| `ERP_MAX_RETRIES` | `3` | Retries after the first request |
| `RETRY_BASE_DELAY` | `0.2` | Exponential backoff base in seconds |

## License

MIT

# UniPack API - NocoDB to Odoo Sync Backend

FastAPI backend that syncs data between NocoDB and Odoo ERP.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/sync/products` | Sync all products from NocoDB to Odoo |
| POST | `/sync/contacts` | Sync all contacts from NocoDB to Odoo |
| POST | `/products` | Create single product in Odoo |
| POST | `/contacts` | Create single contact in Odoo |

## Setup

1. Copy `.env.example` to `.env` and fill in credentials
2. Install: `pip install -r requirements.txt`
3. Run: `uvicorn app.main:app --reload`

## Docker Deployment

```bash
docker-compose up -d --build
```

## API Docs

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

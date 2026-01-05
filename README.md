# UniPack API - NocoDB to Odoo Sync Backend

FastAPI backend for Google Sheets → Odoo integration at `api.unipack.asia`.

## Quick Start with uv

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/sagarsiwach/unipack-server.git
cd unipack-server

# Create venv and install deps (fast!)
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
uv pip install -r requirements.txt

# Configure
cp .env.example .env

# Run
uvicorn app.main:app --reload
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/health` | ❌ | Health check |
| GET | `/api/v1/reference/categories` | ✅ | Product categories |
| GET | `/api/v1/reference/taxes` | ✅ | Sales taxes |
| GET | `/api/v1/reference/countries` | ✅ | Countries |
| POST | `/api/v1/products/batch` | ✅ | Batch create products |
| POST | `/api/v1/customers/batch` | ✅ | Batch create customers |
| POST | `/api/v1/ai/generate-name` | ✅ | AI product names |
| POST | `/api/v1/ai/generate-description` | ✅ | AI descriptions |

**Auth**: `Authorization: Bearer unipack-api-key-2024`

## Docker Deployment

```bash
docker-compose up -d --build
```

## Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

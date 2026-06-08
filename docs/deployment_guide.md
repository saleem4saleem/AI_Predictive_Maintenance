# Deployment Guide

## Local Development

Install and run the backend:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m pytest
python -m uvicorn app.main:app --reload
```

API docs:

```text
http://localhost:8000/docs
```

## Docker Development

From the project root:

```powershell
docker compose up --build
```

This starts:

- FastAPI backend on port `8000`
- TimescaleDB/PostgreSQL on port `5432`

## Environment Variables

Use `.env.example` as the template. Do not store real secrets in source control.

Recommended production-style variables:

```env
ENVIRONMENT=production
API_PREFIX=/api/v1
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DATABASE_URL=postgresql://user:password@host:5432/predictive_maintenance
MODEL_DIR=backend/saved_models
OPENAI_API_KEY=
LLM_PROVIDER=none
ENABLE_LLM=false
USE_MOCK_DATA=false
CORS_ORIGINS=https://your-frontend-host.example
```

## Database Setup

The MVP uses sample data for most endpoints, but the backend is prepared for PostgreSQL/TimescaleDB.

For Docker development, the database is created automatically by `docker compose`.

For a company server:

1. Create the PostgreSQL/TimescaleDB database.
2. Set `DATABASE_URL`.
3. Run migrations when Alembic migrations are added.
4. Keep `/api/v1/health/database` available for debugging.

## Model Files

Model artifacts live under:

```text
backend/saved_models/
```

The active model is selected by:

```text
backend/saved_models/active_model.json
```

Train the MVP model:

```powershell
cd backend
python -m app.ml.train
```

Future model versions should be saved with versioned filenames, then activated through `active_model.json`.

## Logs

For local development, logs are written to stdout/stderr by Uvicorn and Python logging.

For production, route stdout/stderr into the hosting platform log collector.

Important events to monitor:

- Backend startup
- Health endpoint failures
- Database unavailable
- Model registry unavailable
- RAG fallback
- LLM fallback
- Feedback submissions

## Backups

Back up:

- PostgreSQL/TimescaleDB data volume
- `backend/saved_models/`
- imported SAP/work-order/checklist datasets
- technician feedback records

## Frontend Integration Contract

Frontend clients should only depend on `/api/v1` response contracts. Backend internals such as database schema, ML model type, RAG implementation, and feedback storage can change without changing frontend layout.

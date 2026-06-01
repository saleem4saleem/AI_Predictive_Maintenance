# Predictive Maintenance App

Backend-first predictive maintenance prototype for industrial assets in a glass manufacturing line.

## Backend Quick Start

From the project root:

```powershell
cd "C:\Users\salee\OneDrive\Desktop\predictive-maintenance-app\backend"
python -m pip install -r requirements.txt
python -m pytest
python -m app.ml.train
python -m uvicorn app.main:app --reload
```

Open:

- http://localhost:8000/docs
- http://localhost:8000/api/v1/health
- http://localhost:8000/api/v1/overview
- http://localhost:8000/api/v1/models/active

The API base URL is:

```text
http://localhost:8000/api/v1
```

## Helper Scripts

PowerShell:

```powershell
.\scripts\run_backend.ps1
.\scripts\run_tests.ps1
.\scripts\train_model.ps1
.\scripts\check_api.ps1
```

Shell:

```sh
sh scripts/run_backend.sh
sh scripts/run_tests.sh
sh scripts/train_model.sh
```

## Docker

From the project root:

```powershell
docker compose up --build
```

Services:

- Backend: http://localhost:8000
- PostgreSQL/TimescaleDB: localhost:5432

The backend can still serve basic health, overview, asset, prediction, RAG, and feedback endpoints when external services such as the LLM are unavailable.

## Environment

Copy `.env.example` to `.env` for local overrides. Do not commit real secrets.

Important variables:

- `API_PREFIX=/api/v1`
- `BACKEND_PORT=8000`
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/predictive_maintenance`
- `MODEL_DIR=backend/saved_models`
- `OPENAI_API_KEY=`
- `ENABLE_LLM=false`
- `USE_MOCK_DATA=true`
- `CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8501`

## Backend Tests

```powershell
cd backend
python -m pytest
```

The backend test suite protects the `/api/v1` response contracts that the frontend will depend on.

## More Docs

- [Troubleshooting](docs/troubleshooting.md)
- [Deployment Guide](docs/deployment_guide.md)

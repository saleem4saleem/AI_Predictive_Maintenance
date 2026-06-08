# Backend Troubleshooting

## Backend Does Not Start

Use the backend folder as the working directory:

```powershell
cd "C:\Users\salee\OneDrive\Desktop\predictive-maintenance-app\backend"
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

If dependencies are missing, reinstall requirements.

## ModuleNotFoundError

Run commands from `backend/`, or use the helper scripts from the project root:

```powershell
.\scripts\run_backend.ps1
.\scripts\run_tests.ps1
```

The backend test configuration sets `pythonpath = .` for pytest.

## Port 8000 Already Used

Stop the existing backend process, or run with another port:

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

## Model File Missing

The app should not crash if model artifacts are missing. To train the local MVP model:

```powershell
cd backend
python -m app.ml.train
```

Check:

```text
backend/saved_models/active_model.json
```

## Database Unavailable

For MVP development, the backend can use sample/mock data:

```env
USE_MOCK_DATA=true
```

If using Docker database:

```powershell
docker compose up --build
```

Check `DATABASE_URL` and the `/api/v1/health/database` endpoint.

## CORS Errors During Frontend Integration

Confirm `CORS_ORIGINS` contains the frontend URL:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8501
```

Restart the backend after changing environment variables.

## LLM Unavailable

LLM is optional. Without an API key, the backend returns fallback explanations:

```env
OPENAI_API_KEY=
LLM_PROVIDER=none
ENABLE_LLM=false
```

Prediction endpoints should still work.

## API Readiness Check

With the backend running:

```powershell
.\scripts\check_api.ps1
```

This checks health, overview, assets, and active model status.

# Saved Models

This folder is owned by the backend ML layer.

Frontend clients must not read files from this directory. They should call
stable `/api/v1` endpoints only.

Current MVP artifacts:

- `active_model.json`: active model registry metadata
- `isolation_forest_v1.joblib`: trained Isolation Forest artifact
- `scaler_v1.joblib`: StandardScaler artifact

The frontend must never read files in this folder. It should call
`/api/v1/models/active` or prediction endpoints instead. Model artifacts can be
replaced, versioned, or retired behind the backend registry without changing the
frontend contract.

Future model artifact names should include the model family and version, for
example `xgboost_v2.joblib` or `lstm_rul_v1.joblib`, then `active_model.json`
can be updated to activate that model.

Regenerate artifacts from the backend folder:

```powershell
python -m app.ml.train
```

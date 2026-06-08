from app.services.prediction_orchestrator import run_prediction


def run_prediction_job(asset_ids: list[str]) -> list:
    return [run_prediction(asset_id) for asset_id in asset_ids]

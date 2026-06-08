from app.services.sensor_service import get_sensor_history_rows


def run_data_quality_job(asset_id: str) -> dict:
    rows = get_sensor_history_rows(asset_id)
    return {"asset_id": asset_id, "sample_rows": len(rows), "status": "ok" if rows else "missing_data"}

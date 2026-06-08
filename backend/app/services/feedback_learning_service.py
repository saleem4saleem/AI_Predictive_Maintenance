from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.core.config import PROJECT_ROOT
from app.services.asset_service import get_asset
from app.utils.logging_utils import log_feedback_saved, log_feedback_storage_fallback

FEEDBACK_PATH = PROJECT_ROOT / "data" / "sample" / "sample_feedback.csv"

FEEDBACK_FIELDNAMES = [
    "feedback_id",
    "asset_id",
    "asset_code",
    "prediction_id",
    "feedback_date",
    "was_prediction_correct",
    "actual_failure_happened",
    "actual_failure_mode",
    "action_taken",
    "timing_feedback",
    "technician_comment",
]


def prepare_feedback_record(feedback_data: dict[str, Any]) -> dict[str, Any]:
    """Normalize technician feedback into a training-ready record.

    CSV is the MVP fallback. A later PostgreSQL implementation can store this
    same record shape without changing the API contract.
    """

    asset_id = int(feedback_data["asset_id"])
    try:
        asset_code = get_asset(asset_id).asset_code
    except Exception:
        asset_code = None

    return {
        "feedback_id": feedback_data.get("feedback_id") or _new_feedback_id(),
        "asset_id": asset_id,
        "asset_code": asset_code,
        "prediction_id": feedback_data.get("prediction_id"),
        "feedback_date": feedback_data.get("feedback_date") or _utc_timestamp(),
        "was_prediction_correct": feedback_data.get("was_prediction_correct"),
        "actual_failure_happened": feedback_data.get("actual_failure_happened"),
        "actual_failure_mode": feedback_data.get("actual_failure_mode"),
        "action_taken": feedback_data.get("action_taken"),
        "timing_feedback": feedback_data.get("timing_feedback"),
        "technician_comment": feedback_data.get("technician_comment"),
    }


def save_feedback_record(
    feedback_record: dict[str, Any],
    storage_path: str | Path | None = None,
) -> dict[str, Any]:
    """Append feedback to the CSV fallback store."""

    path = Path(storage_path or FEEDBACK_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    _ensure_feedback_file(path)

    with path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FEEDBACK_FIELDNAMES)
        writer.writerow(_serialize_record(feedback_record))

    log_feedback_saved(str(feedback_record["feedback_id"]))
    return {
        "status": "saved",
        "feedback_id": feedback_record["feedback_id"],
        "path": str(path),
    }


def get_feedback_summary(
    asset_id: int | None = None,
    storage_path: str | Path | None = None,
) -> dict[str, Any]:
    records = get_training_feedback_records(storage_path=storage_path)
    if asset_id is not None:
        records = [record for record in records if _to_int(record.get("asset_id")) == int(asset_id)]

    return {
        "asset_id": asset_id,
        "total_feedback": len(records),
        "correct_predictions": sum(_to_bool(record.get("was_prediction_correct")) is True for record in records),
        "incorrect_predictions": sum(_to_bool(record.get("was_prediction_correct")) is False for record in records),
        "actual_failures_reported": sum(_to_bool(record.get("actual_failure_happened")) is True for record in records),
        "timing_too_early": sum(record.get("timing_feedback") == "too_early" for record in records),
        "timing_correct": sum(record.get("timing_feedback") == "correct" for record in records),
        "timing_too_late": sum(record.get("timing_feedback") == "too_late" for record in records),
    }


def get_training_feedback_records(storage_path: str | Path | None = None) -> list[dict[str, Any]]:
    path = Path(storage_path or FEEDBACK_PATH)
    if not path.exists():
        return []

    try:
        with path.open("r", newline="", encoding="utf-8") as csv_file:
            return [_deserialize_record(row) for row in csv.DictReader(csv_file)]
    except OSError as exc:
        log_feedback_storage_fallback(f"Unable to read feedback CSV: {exc}")
        return []


def prepare_feedback_for_training(feedback_data: Any) -> dict[str, Any]:
    """Compatibility helper used by older tests and services."""

    if hasattr(feedback_data, "model_dump"):
        feedback_data = feedback_data.model_dump()
    record = prepare_feedback_record(dict(feedback_data))
    return {
        "asset_id": record["asset_id"],
        "prediction_id": record["prediction_id"],
        "label_prediction_correct": record["was_prediction_correct"],
        "label_failure_happened": record["actual_failure_happened"],
        "actual_failure_mode": record["actual_failure_mode"],
        "action_taken": record["action_taken"],
        "timing_feedback": record["timing_feedback"],
        "technician_comment": record["technician_comment"],
    }


def _ensure_feedback_file(path: Path) -> None:
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as csv_file:
            csv.DictWriter(csv_file, fieldnames=FEEDBACK_FIELDNAMES).writeheader()
        return

    with path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        existing_rows = list(reader)
        existing_fields = reader.fieldnames or []

    if existing_fields == FEEDBACK_FIELDNAMES:
        return

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FEEDBACK_FIELDNAMES)
        writer.writeheader()
        for row in existing_rows:
            writer.writerow(_serialize_record(_deserialize_record(row)))


def _serialize_record(record: dict[str, Any]) -> dict[str, str]:
    return {
        field: _serialize_value(record.get(field))
        for field in FEEDBACK_FIELDNAMES
    }


def _deserialize_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedback_id": record.get("feedback_id"),
        "asset_id": _to_int(record.get("asset_id")),
        "asset_code": record.get("asset_code") or None,
        "prediction_id": record.get("prediction_id") or None,
        "feedback_date": record.get("feedback_date") or None,
        "was_prediction_correct": _to_bool(record.get("was_prediction_correct")),
        "actual_failure_happened": _to_bool(record.get("actual_failure_happened")),
        "actual_failure_mode": record.get("actual_failure_mode") or None,
        "action_taken": record.get("action_taken") or None,
        "timing_feedback": record.get("timing_feedback") or None,
        "technician_comment": record.get("technician_comment") or None,
    }


def _serialize_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _to_bool(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _to_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _new_feedback_id() -> str:
    return f"FB-{uuid4().hex[:8].upper()}"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

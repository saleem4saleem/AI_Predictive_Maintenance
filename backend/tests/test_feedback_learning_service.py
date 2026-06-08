from __future__ import annotations

from app.services.feedback_learning_service import (
    get_feedback_summary,
    get_training_feedback_records,
    prepare_feedback_record,
    save_feedback_record,
)


def test_prepare_feedback_record_adds_learning_fields() -> None:
    record = prepare_feedback_record(
        {
            "asset_id": 6,
            "prediction_id": 101,
            "was_prediction_correct": True,
            "actual_failure_happened": True,
            "actual_failure_mode": "suction cup wear",
            "action_taken": "Replaced suction cups",
            "timing_feedback": "correct",
            "technician_comment": "Useful prediction",
        }
    )

    assert record["feedback_id"].startswith("FB-")
    assert record["asset_code"] == "PACKAGING_001"
    assert record["feedback_date"]
    assert record["was_prediction_correct"] is True


def test_save_feedback_record_writes_csv_and_summary(tmp_path) -> None:
    feedback_path = tmp_path / "feedback.csv"
    record = prepare_feedback_record(
        {
            "asset_id": 3,
            "prediction_id": 202,
            "was_prediction_correct": False,
            "actual_failure_happened": True,
            "actual_failure_mode": "bearing wear",
            "action_taken": "Replaced bearing",
            "timing_feedback": "too_late",
            "technician_comment": "Failure happened before inspection",
        }
    )

    result = save_feedback_record(record, storage_path=feedback_path)
    records = get_training_feedback_records(storage_path=feedback_path)
    summary = get_feedback_summary(storage_path=feedback_path)

    assert result["status"] == "saved"
    assert len(records) == 1
    assert summary["total_feedback"] == 1
    assert summary["incorrect_predictions"] == 1
    assert summary["actual_failures_reported"] == 1
    assert summary["timing_too_late"] == 1


def test_missing_feedback_file_returns_empty_summary(tmp_path) -> None:
    missing_path = tmp_path / "missing.csv"

    assert get_training_feedback_records(storage_path=missing_path) == []
    assert get_feedback_summary(storage_path=missing_path)["total_feedback"] == 0

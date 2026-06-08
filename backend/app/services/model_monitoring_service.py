from __future__ import annotations

from app.ml.model_registry import ModelRegistry
from app.services.feedback_learning_service import get_feedback_summary


def get_active_model_status() -> dict:
    status = ModelRegistry().get_public_model_status()
    feedback_metrics = get_feedback_metrics()
    status.setdefault("metrics", {})
    status.setdefault("metadata_available", False)
    status.setdefault("model_file_exists", False)
    status.setdefault("scaler_file_exists", False)
    status["metrics"] = {
        "prediction_count": 0,
        "feedback_count": feedback_metrics["total_feedback"],
        "correct_predictions": feedback_metrics["correct_predictions"],
        "false_alarms": feedback_metrics["false_alarms"],
        "missed_failures": feedback_metrics["missed_failures"],
        "average_confidence": "not_enough_data",
        "data_drift_warning": False,
    }
    return status


def get_feedback_metrics() -> dict:
    """Return simple feedback-derived metrics for model monitoring.

    These metrics are CSV-backed for the MVP and can later come from a model
    monitoring table without changing callers.
    """

    summary = get_feedback_summary()
    false_alarms = max(
        summary["incorrect_predictions"] - summary["actual_failures_reported"],
        0,
    )
    missed_failures = summary["timing_too_late"]
    return {
        "total_feedback": summary["total_feedback"],
        "correct_predictions": summary["correct_predictions"],
        "incorrect_predictions": summary["incorrect_predictions"],
        "actual_failures_reported": summary["actual_failures_reported"],
        "timing_too_early": summary["timing_too_early"],
        "timing_correct": summary["timing_correct"],
        "timing_too_late": summary["timing_too_late"],
        "false_alarms": false_alarms,
        "missed_failures": missed_failures,
    }

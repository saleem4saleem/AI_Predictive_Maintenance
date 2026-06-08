from __future__ import annotations

from app.services.model_monitoring_service import get_active_model_status, get_feedback_metrics


def test_feedback_metrics_use_sample_feedback_data() -> None:
    metrics = get_feedback_metrics()

    assert metrics["total_feedback"] >= 10
    assert metrics["correct_predictions"] >= 1
    assert metrics["actual_failures_reported"] >= 1
    assert {"timing_too_early", "timing_correct", "timing_too_late"} <= set(metrics)


def test_active_model_status_includes_feedback_metrics() -> None:
    status = get_active_model_status()

    assert "metrics" in status
    assert "feedback_count" in status["metrics"]
    assert status["metrics"]["feedback_count"] >= 10

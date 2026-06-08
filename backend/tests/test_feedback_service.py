from __future__ import annotations

import pytest

import app.services.feedback_service as feedback_service
from app.exceptions import InvalidRequestError
from app.services.feedback_service import submit_feedback


def test_feedback_service_accepts_valid_dict_payload(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(feedback_service, "FEEDBACK_PATH", tmp_path / "feedback.csv")

    response = submit_feedback(
        {
            "asset_id": 6,
            "prediction_id": 101,
            "was_prediction_correct": True,
            "actual_failure_happened": True,
            "actual_failure_mode": "suction cup wear",
            "action_taken": "Replaced suction cups",
            "timing_feedback": "correct",
            "technician_comment": "",
        }
    )

    assert response.status == "accepted"
    assert response.asset_id == 6
    assert response.feedback_id.startswith("FB-")
    assert (tmp_path / "feedback.csv").exists()


def test_feedback_service_rejects_invalid_timing_feedback(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(feedback_service, "FEEDBACK_PATH", tmp_path / "feedback.csv")

    with pytest.raises(InvalidRequestError):
        submit_feedback(
            {
                "asset_id": 6,
                "timing_feedback": "soon",
            }
        )


def test_feedback_service_validates_asset_exists(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(feedback_service, "FEEDBACK_PATH", tmp_path / "feedback.csv")

    with pytest.raises(Exception):
        submit_feedback(
            {
                "asset_id": 999999,
                "timing_feedback": "not_applicable",
            }
        )

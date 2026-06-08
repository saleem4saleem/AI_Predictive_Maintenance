from fastapi.testclient import TestClient

import app.services.feedback_service as feedback_service
from app.main import app


client = TestClient(app)


def test_feedback_endpoint_accepts_payload(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(feedback_service, "FEEDBACK_PATH", tmp_path / "feedback.csv")
    response = client.post(
        "/api/v1/feedback",
        json={
            "asset_id": "6",
            "prediction_id": "PRED-TEST",
            "was_prediction_correct": True,
            "actual_failure_happened": False,
            "actual_failure_mode": "worn suction cups",
            "action_taken": "Replaced suction cups",
            "timing_feedback": "correct",
            "technician_comment": "Useful prediction",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["feedback_id"].startswith("FB-")

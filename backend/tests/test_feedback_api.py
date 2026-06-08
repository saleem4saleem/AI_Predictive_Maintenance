from fastapi.testclient import TestClient

import app.services.feedback_service as feedback_service
from app.main import app


client = TestClient(app)


def test_rag_search_api_returns_placeholder_results() -> None:
    response = client.post(
        "/api/v1/rag/search",
        json={"query": "high vibration bearing failure", "asset_id": "3"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "high vibration bearing failure"
    assert payload["results"]
    assert {"source_type", "title", "summary", "score"} <= set(payload["results"][0])


def test_feedback_api_accepts_future_learning_payload(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(feedback_service, "FEEDBACK_PATH", tmp_path / "feedback.csv")
    response = client.post(
        "/api/v1/feedback",
        json={
            "asset_id": "1",
            "prediction_id": "PRED-001",
            "was_prediction_correct": True,
            "actual_failure_happened": False,
            "actual_failure_mode": None,
            "action_taken": "Continued monitoring",
            "timing_feedback": "correct",
            "technician_comment": "API payload accepted for future learning.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "accepted"
    assert payload["message"] == "Feedback received successfully"
    assert payload["asset_id"] == 1


def test_feedback_api_rejects_invalid_timing_feedback() -> None:
    response = client.post(
        "/api/v1/feedback",
        json={
            "asset_id": 6,
            "timing_feedback": "later",
        },
    )

    assert response.status_code == 422

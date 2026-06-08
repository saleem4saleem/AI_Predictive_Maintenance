from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_rag_api_returns_required_fields() -> None:
    response = client.post(
        "/api/v1/rag/search",
        json={"query": "high vibration bearing failure", "asset_id": 3},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "high vibration bearing failure"
    assert payload["results"]
    result = payload["results"][0]
    assert {"source_type", "title", "summary", "score"} <= set(result)


def test_rag_api_no_match_returns_empty_results() -> None:
    response = client.post(
        "/api/v1/rag/search",
        json={"query": "zzznomatchterm", "asset_id": 1},
    )

    assert response.status_code == 200
    assert response.json()["results"] == []


def test_rag_api_rejects_empty_query_cleanly() -> None:
    response = client.post(
        "/api/v1/rag/search",
        json={"query": "", "asset_id": 1},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"

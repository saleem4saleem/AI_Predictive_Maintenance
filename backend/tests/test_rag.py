from app.services.rag_service import search_knowledge


def test_rag_keyword_fallback_returns_results() -> None:
    response = search_knowledge("bearing lubrication vibration", asset_id="3", limit=3)
    assert response.query == "bearing lubrication vibration"
    assert response.results
    assert response.results[0].score > 0

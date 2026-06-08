from app.contracts.rag_contract import RagSearchResponse
from app.services.rag_service import search_knowledge


def test_rag_service_returns_contract_response() -> None:
    response = search_knowledge("high vibration bearing failure", asset_id=3)

    assert isinstance(response, RagSearchResponse)
    assert response.query == "high vibration bearing failure"
    assert response.results
    assert response.results[0].source_type in {"expert_note", "work_order", "checklist"}


def test_rag_service_no_match_is_safe_empty_result() -> None:
    response = search_knowledge("zzznomatchterm", asset_id=1)

    assert response.results == []

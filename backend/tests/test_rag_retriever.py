from app.rag.retriever import search_documents


def test_search_high_vibration_bearing_returns_relevant_result() -> None:
    results = search_documents("high vibration bearing failure", top_k=5)

    assert results
    combined = " ".join(f"{item['title']} {item['content']}".lower() for item in results)
    assert "bearing" in combined or "vibration" in combined


def test_search_suction_cup_returns_packaging_result() -> None:
    results = search_documents("suction cup vacuum", asset_id=6, top_k=5)

    assert results
    assert all(item["asset_id"] == 6 for item in results)
    combined = " ".join(f"{item['title']} {item['content']}".lower() for item in results)
    assert "suction" in combined or "vacuum" in combined


def test_asset_id_filter_limits_results() -> None:
    results = search_documents("bearing vibration", asset_id=3, top_k=5)

    assert results
    assert all(item["asset_id"] == 3 for item in results)


def test_no_match_query_returns_empty_results() -> None:
    results = search_documents("zzznomatchterm", top_k=5)

    assert results == []

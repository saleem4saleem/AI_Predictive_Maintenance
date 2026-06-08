from __future__ import annotations

import re
from typing import Any

from app.rag.chunking import chunk_documents
from app.rag.document_cleaner import build_searchable_text
from app.rag.document_loader import load_all_documents


def search_documents(query: str, asset_id: int | None = None, top_k: int = 5) -> list[dict[str, Any]]:
    """MVP keyword retriever.

    This function can later be replaced internally with pgvector or Chroma while
    rag_service keeps the same response contract.
    """

    terms = _query_terms(query)
    if not terms:
        return []

    chunks = chunk_documents(load_all_documents())
    scored: list[dict[str, Any]] = []
    for document in chunks:
        if asset_id is not None and document.get("asset_id") != asset_id:
            continue

        score = _score_document(document, terms, asset_id)
        if score <= 0:
            continue
        scored.append({**document, "score": round(score, 3)})

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


def keyword_search(query: str, asset_id: str | int | None = None, limit: int = 5) -> list[dict[str, Any]]:
    normalized_asset_id = int(asset_id) if str(asset_id or "").isdigit() else None
    return search_documents(query, asset_id=normalized_asset_id, top_k=limit)


def _query_terms(query: str) -> list[str]:
    return [
        term
        for term in re.findall(r"[a-zA-Z0-9_]+", query.lower())
        if len(term) > 2
    ]


def _score_document(document: dict[str, Any], terms: list[str], asset_id: int | None) -> float:
    searchable = build_searchable_text(document)
    title = str(document.get("title", "")).lower()
    metadata_text = " ".join(str(value).lower() for value in (document.get("metadata") or {}).values())

    score = 0.0
    for term in terms:
        content_matches = searchable.count(term)
        title_matches = title.count(term)
        metadata_matches = metadata_text.count(term)
        score += content_matches
        score += title_matches * 2.0
        score += metadata_matches * 0.5

    if asset_id is not None and document.get("asset_id") == asset_id:
        score *= 1.25
    return score

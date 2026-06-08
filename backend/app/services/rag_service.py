from __future__ import annotations

from app.contracts.rag_contract import RagResultContract, RagSearchResponseContract
from app.rag.retriever import search_documents


def search_knowledge(query: str, asset_id: int | str | None = None, limit: int = 5) -> RagSearchResponseContract:
    try:
        normalized_asset_id = int(asset_id) if str(asset_id or "").isdigit() else None
        results = [
            RagResultContract(
                source_type=item["source_type"],
                title=item["title"],
                summary=item["content"],
                score=float(item["score"]),
            )
            for item in search_documents(query, asset_id=normalized_asset_id, top_k=limit)
        ]
    except Exception:
        results = []
    return RagSearchResponseContract(query=query, results=results)

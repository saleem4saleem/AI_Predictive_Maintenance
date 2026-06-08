from __future__ import annotations

from fastapi import APIRouter

from app.contracts.rag_contract import RagSearchRequest, RagSearchResponse
from app.services.rag_service import search_knowledge

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/search", response_model=RagSearchResponse)
async def search_rag(request: RagSearchRequest) -> RagSearchResponse:
    return search_knowledge(request.query, asset_id=request.asset_id, limit=request.limit)

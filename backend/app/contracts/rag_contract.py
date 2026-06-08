from __future__ import annotations

from pydantic import BaseModel, Field


class RagSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    asset_id: int | None = None
    limit: int = Field(default=5, ge=1, le=20)


class RagSearchResult(BaseModel):
    source_type: str
    title: str
    summary: str
    score: float | None = None


class RagSearchResponse(BaseModel):
    query: str
    results: list[RagSearchResult]


RagSearchRequestContract = RagSearchRequest
RagResultContract = RagSearchResult
RagSearchResponseContract = RagSearchResponse

from __future__ import annotations

from typing import Any


def chunk_text(text: str, max_words: int = 120) -> list[str]:
    words = text.split()
    if not words:
        return []
    return [
        " ".join(words[index : index + max_words])
        for index in range(0, len(words), max_words)
    ]


def chunk_documents(documents: list[dict[str, Any]], max_words: int = 120) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    for document in documents:
        text_chunks = chunk_text(document.get("content", ""), max_words=max_words)
        if not text_chunks:
            text_chunks = [""]
        for index, content in enumerate(text_chunks, start=1):
            chunks.append(
                {
                    "document_id": document.get("document_id"),
                    "chunk_id": f"{document.get('document_id')}-chunk-{index}",
                    "asset_id": document.get("asset_id"),
                    "asset_code": document.get("asset_code"),
                    "source_type": document.get("source_type"),
                    "title": document.get("title"),
                    "content": content,
                    "metadata": document.get("metadata", {}),
                }
            )
    return chunks

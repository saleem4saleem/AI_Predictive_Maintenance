from __future__ import annotations

from typing import Any


def clean_text(text: str | None) -> str:
    """Normalize text for MVP keyword search."""

    return " ".join(str(text or "").replace("\n", " ").split())


def build_searchable_text(document: dict[str, Any]) -> str:
    """Combine title, content, metadata, and identifiers into searchable text."""

    metadata = document.get("metadata") or {}
    metadata_text = " ".join(clean_text(value) for value in metadata.values())
    return clean_text(
        " ".join(
            [
                document.get("asset_code", ""),
                document.get("source_type", ""),
                document.get("title", ""),
                document.get("content", ""),
                metadata_text,
            ]
        )
    ).lower()

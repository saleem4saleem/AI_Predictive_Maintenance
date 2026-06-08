from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from app.core.config import PROJECT_ROOT
from app.rag.document_cleaner import clean_text

SAMPLE_DATA_DIR = PROJECT_ROOT / "data" / "sample"
EXPERT_NOTES_PATH = SAMPLE_DATA_DIR / "sample_expert_notes.csv"
WORK_ORDERS_PATH = SAMPLE_DATA_DIR / "sample_work_orders.csv"
CHECKLISTS_PATH = SAMPLE_DATA_DIR / "sample_checklists.csv"


def load_expert_notes_documents(path: Path | None = None) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for row in _read_csv_rows(path or EXPERT_NOTES_PATH):
        documents.append(
            _document(
                document_id=row.get("note_id") or "",
                asset_id=row.get("asset_id"),
                asset_code=row.get("asset_code"),
                source_type="expert_note",
                title=row.get("title") or f"Expert note {row.get('note_id', '')}",
                content=" ".join(
                    [
                        row.get("component", ""),
                        row.get("symptom", row.get("symptoms", "")),
                        row.get("known_cause", row.get("cause", "")),
                        row.get("recommended_action", ""),
                        row.get("technician_note", ""),
                        row.get("summary", ""),
                    ]
                ),
                metadata={
                    "component": row.get("component"),
                    "known_cause": row.get("known_cause") or row.get("cause"),
                    "recommended_action": row.get("recommended_action"),
                    "created_by": row.get("created_by"),
                    "created_at": row.get("created_at"),
                },
            )
        )
    return documents


def load_work_order_documents(path: Path | None = None) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for row in _read_csv_rows(path or WORK_ORDERS_PATH):
        documents.append(
            _document(
                document_id=row.get("work_order_id") or row.get("sap_order_number") or "",
                asset_id=row.get("asset_id"),
                asset_code=row.get("asset_code"),
                source_type="work_order",
                title=row.get("title") or f"Work order {row.get('sap_order_number') or row.get('work_order_id', '')}",
                content=" ".join(
                    [
                        row.get("failure_description", ""),
                        row.get("failure_cause", ""),
                        row.get("failure_mode", ""),
                        row.get("summary", ""),
                        row.get("action_taken", ""),
                        row.get("replaced_part", ""),
                        row.get("technician_notes", ""),
                    ]
                ),
                metadata={
                    "sap_order_number": row.get("sap_order_number"),
                    "order_type": row.get("order_type"),
                    "priority": row.get("priority"),
                    "downtime_hours": row.get("downtime_hours"),
                    "completed_date": row.get("completed_date"),
                },
            )
        )
    return documents


def load_checklist_documents(path: Path | None = None) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for row in _read_csv_rows(path or CHECKLISTS_PATH):
        documents.append(
            _document(
                document_id=row.get("checklist_id") or "",
                asset_id=row.get("asset_id"),
                asset_code=row.get("asset_code"),
                source_type="checklist",
                title=row.get("title") or row.get("checklist_name") or "Maintenance checklist",
                content=" ".join(
                    [
                        row.get("checklist_item", ""),
                        row.get("checklist_name", ""),
                        row.get("task_description", ""),
                        row.get("summary", ""),
                        row.get("safety_note", ""),
                    ]
                ),
                metadata={
                    "frequency": row.get("frequency"),
                    "responsible_role": row.get("responsible_role"),
                    "estimated_minutes": row.get("estimated_minutes"),
                },
            )
        )
    return documents


def load_all_documents() -> list[dict[str, Any]]:
    return [
        *load_expert_notes_documents(),
        *load_work_order_documents(),
        *load_checklist_documents(),
    ]


def load_sample_documents() -> list[dict[str, Any]]:
    """Backward-compatible alias for older tests/services."""

    return load_all_documents()


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def _document(
    *,
    document_id: str,
    asset_id: str | None,
    asset_code: str | None,
    source_type: str,
    title: str,
    content: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "document_id": clean_text(document_id),
        "asset_id": int(asset_id) if str(asset_id or "").isdigit() else None,
        "asset_code": clean_text(asset_code),
        "source_type": source_type,
        "title": clean_text(title),
        "content": clean_text(content),
        "metadata": {key: clean_text(value) for key, value in metadata.items() if value not in {None, ""}},
    }

from app.rag.chunking import chunk_documents, chunk_text
from app.rag.document_cleaner import build_searchable_text, clean_text
from app.rag.document_loader import (
    load_all_documents,
    load_checklist_documents,
    load_expert_notes_documents,
    load_work_order_documents,
)


def test_document_loader_loads_sample_sources() -> None:
    expert_notes = load_expert_notes_documents()
    work_orders = load_work_order_documents()
    checklists = load_checklist_documents()

    assert expert_notes
    assert work_orders
    assert checklists
    assert {doc["source_type"] for doc in load_all_documents()} >= {"expert_note", "work_order", "checklist"}


def test_document_cleaner_normalizes_text_and_search_content() -> None:
    assert clean_text(" bearing   wear\n detected ") == "bearing wear detected"
    searchable = build_searchable_text(
        {
            "asset_code": "PACKAGING_001",
            "source_type": "expert_note",
            "title": "Suction Cup Wear",
            "content": "Vacuum issue",
            "metadata": {"cause": "hose leakage"},
        }
    )

    assert "packaging_001" in searchable
    assert "suction cup wear" in searchable
    assert "hose leakage" in searchable


def test_chunking_keeps_document_metadata() -> None:
    chunks = chunk_text(" ".join(str(index) for index in range(250)), max_words=100)
    assert len(chunks) == 3

    documents = [
        {
            "document_id": "DOC-1",
            "asset_id": 1,
            "asset_code": "FURNACE_001",
            "source_type": "expert_note",
            "title": "Long note",
            "content": " ".join(str(index) for index in range(130)),
            "metadata": {"component": "bearing"},
        }
    ]
    chunked_documents = chunk_documents(documents, max_words=120)

    assert len(chunked_documents) == 2
    assert chunked_documents[0]["document_id"] == "DOC-1"
    assert chunked_documents[0]["asset_code"] == "FURNACE_001"

from app.rag.document_loader import load_sample_documents


def run_rag_indexing_job() -> dict:
    documents = load_sample_documents()
    return {"indexed_documents": len(documents), "mode": "keyword_fallback"}

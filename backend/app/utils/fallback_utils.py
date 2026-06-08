LLM_FALLBACK_EXPLANATION = (
    "The prediction is based on sensor behavior, maintenance rules, and available maintenance history. "
    "A detailed AI explanation is temporarily unavailable."
)


def get_default_ai_explanation(context: dict | None = None) -> dict:
    from app.services.llm_service import generate_fallback_explanation

    return {
        "summary": generate_fallback_explanation(context),
        "confidence": "low",
        "fallback_used": True,
    }


def empty_rag_result() -> list:
    return []

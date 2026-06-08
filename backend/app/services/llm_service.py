from __future__ import annotations

from typing import Any

from app.core.config import get_settings
from app.utils.fallback_utils import LLM_FALLBACK_EXPLANATION
from app.utils.logging_utils import (
    log_llm_explanation_generated,
    log_llm_failure,
    log_llm_fallback_used,
    log_llm_unavailable,
)

IMPLEMENTED_LLM_PROVIDERS: set[str] = set()


def is_llm_available() -> bool:
    """Return whether an external LLM provider is ready to generate text.

    This MVP intentionally has no provider implementation. When a provider is
    added later, this function can become the switch without changing frontend
    contracts or prediction response shapes.
    """

    settings = get_settings()
    if not settings.enable_llm:
        log_llm_unavailable("ENABLE_LLM is false.")
        return False
    if not settings.openai_api_key:
        log_llm_unavailable("OPENAI_API_KEY is missing.")
        return False
    if settings.llm_provider.lower() not in IMPLEMENTED_LLM_PROVIDERS:
        log_llm_unavailable(f"LLM provider '{settings.llm_provider}' is not implemented.")
        return False
    return True


def generate_prediction_explanation(context: dict[str, Any]) -> str:
    """Generate a human-readable explanation.

    For now this safely uses the fallback. Future external provider calls should
    use only the supplied context and must not decide risk.
    """

    if not is_llm_available():
        log_llm_fallback_used("LLM provider unavailable.")
        return generate_fallback_explanation(context)

    try:
        # Provider integration belongs here in a later phase.
        log_llm_explanation_generated(get_settings().llm_provider)
        return generate_fallback_explanation(context)
    except Exception as exc:
        log_llm_failure(exc)
        return generate_fallback_explanation(context)


def generate_fallback_explanation(context: dict[str, Any] | None = None) -> str:
    """Create a useful explanation using only provided backend context."""

    context = context or {}
    if not context:
        return LLM_FALLBACK_EXPLANATION

    parts: list[str] = []
    asset_name = context.get("asset_name")
    risk_level = context.get("risk_level")
    if asset_name or risk_level:
        parts.append(
            f"{asset_name or 'The asset'} is currently classified as {risk_level or 'unknown'} risk."
        )

    sensor_phrase = _sensor_phrase(context.get("sensor_summary"))
    if sensor_phrase:
        parts.append(sensor_phrase)

    failure_mode = context.get("predicted_failure_mode")
    likely_causes = _as_list(context.get("likely_causes"))
    if failure_mode:
        parts.append(f"The likely issue is {failure_mode}.")
    elif likely_causes:
        parts.append(f"Likely causes include {', '.join(likely_causes[:3])}.")

    rule_findings = _as_list(context.get("rule_findings"))
    if rule_findings:
        parts.append(f"Rules found: {'; '.join(rule_findings[:2])}.")

    recommended_actions = _as_list(context.get("recommended_actions"))
    if recommended_actions:
        parts.append(f"Recommended action: {recommended_actions[0]}.")

    remaining_days = context.get("remaining_useful_life_days")
    predicted_date = context.get("predicted_failure_date")
    if remaining_days is not None:
        parts.append(f"Estimated remaining useful life is {remaining_days} days.")
    elif predicted_date:
        parts.append(f"Predicted failure date is {predicted_date}.")

    if not parts:
        return LLM_FALLBACK_EXPLANATION

    return " ".join(parts) + " " + LLM_FALLBACK_EXPLANATION


def explain_prediction(
    context: dict[str, Any] | Any,
    risk_level: str | None = None,
    failure_mode: str | None = None,
    recommendation: str | None = None,
) -> dict[str, Any] | str:
    """Explain a prediction without making the risk decision.

    New code should call this with a context dictionary and receives:
    {"summary": str, "confidence": str, "fallback_used": bool}.

    Older orchestrator code still calls explain_prediction(asset, risk, mode,
    recommendation) and receives a plain string for compatibility.
    """

    if isinstance(context, dict) and risk_level is None:
        try:
            summary = generate_prediction_explanation(context)
            return {
                "summary": summary,
                "confidence": _confidence_from_context(context),
                "fallback_used": not is_llm_available(),
            }
        except Exception as exc:
            log_llm_failure(exc)
            return {
                "summary": generate_fallback_explanation(context),
                "confidence": "low",
                "fallback_used": True,
            }

    legacy_context = {
        "asset_name": getattr(context, "asset_name", None),
        "risk_level": risk_level,
        "predicted_failure_mode": failure_mode,
        "recommended_actions": [recommendation] if recommendation else [],
    }
    return generate_fallback_explanation(legacy_context)


def _sensor_phrase(sensor_summary: Any) -> str | None:
    if not isinstance(sensor_summary, dict):
        return None

    elevated: list[str] = []
    for field in ["vibration", "temperature", "pressure", "current_value", "speed", "flow"]:
        value = sensor_summary.get(field)
        if value is not None:
            elevated.append(f"{field.replace('_', ' ')}={value}")
    if not elevated:
        return None
    return "Current sensor context: " + ", ".join(elevated[:4]) + "."


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item]
    return [str(value)]


def _confidence_from_context(context: dict[str, Any]) -> str:
    confidence = str(context.get("confidence") or "").lower()
    if confidence in {"low", "medium", "high"}:
        return confidence
    if context.get("similar_failures") and context.get("rule_findings"):
        return "medium"
    return "low"

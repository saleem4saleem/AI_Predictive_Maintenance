from __future__ import annotations

from dataclasses import dataclass

from app.core.config import get_settings
from app.services.llm_service import (
    explain_prediction,
    generate_fallback_explanation,
    is_llm_available,
)


def test_llm_is_unavailable_when_disabled(monkeypatch):
    monkeypatch.setenv("ENABLE_LLM", "false")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()

    assert is_llm_available() is False

    get_settings.cache_clear()


def test_fallback_explanation_is_non_empty_without_context():
    explanation = generate_fallback_explanation()

    assert explanation
    assert "sensor behavior" in explanation


def test_fallback_explanation_uses_provided_context_only():
    explanation = generate_fallback_explanation(
        {
            "asset_name": "Packaging Machine",
            "risk_level": "high",
            "predicted_failure_mode": "suction cup wear",
            "recommended_actions": ["Inspect suction cups", "Check vacuum lines"],
        }
    )

    assert "Packaging Machine" in explanation
    assert "high" in explanation
    assert "suction cup wear" in explanation
    assert "Inspect suction cups" in explanation


def test_explain_prediction_returns_structured_fallback(monkeypatch):
    monkeypatch.setenv("ENABLE_LLM", "false")
    get_settings.cache_clear()

    result = explain_prediction(
        {
            "asset_name": "Packaging Machine",
            "risk_level": "high",
            "predicted_failure_mode": "suction cup wear",
            "recommended_actions": ["Inspect suction cups"],
        }
    )

    assert result["summary"]
    assert result["confidence"] in {"low", "medium", "high"}
    assert result["fallback_used"] is True

    get_settings.cache_clear()


def test_explain_prediction_handles_empty_context(monkeypatch):
    monkeypatch.setenv("ENABLE_LLM", "false")
    get_settings.cache_clear()

    result = explain_prediction({})

    assert result["summary"]
    assert result["confidence"] == "low"
    assert result["fallback_used"] is True

    get_settings.cache_clear()


def test_explain_prediction_keeps_legacy_string_signature():
    @dataclass
    class Asset:
        asset_name: str

    explanation = explain_prediction(
        Asset(asset_name="Furnace"),
        "medium",
        "overheating",
        "Check cooling system",
    )

    assert isinstance(explanation, str)
    assert "Furnace" in explanation
    assert "overheating" in explanation
    assert "Check cooling system" in explanation

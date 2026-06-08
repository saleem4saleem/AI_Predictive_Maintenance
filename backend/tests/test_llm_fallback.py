from __future__ import annotations

from app.services.asset_detail_service import get_asset_detail
from app.services.prediction_orchestrator import run_prediction
from app.utils.fallback_utils import get_default_ai_explanation


def test_default_ai_explanation_returns_frontend_friendly_shape():
    result = get_default_ai_explanation(
        {
            "asset_name": "Packaging Machine",
            "risk_level": "high",
            "recommended_actions": ["Inspect suction cups"],
        }
    )

    assert result["summary"]
    assert result["confidence"] == "low"
    assert result["fallback_used"] is True


def test_asset_detail_ai_explanation_uses_safe_fallback():
    detail = get_asset_detail(6)

    assert detail.ai_explanation.summary
    assert detail.ai_explanation.confidence in {"low", "medium", "high"}
    assert detail.ai_explanation.fallback_used is True


def test_prediction_orchestrator_still_returns_explanation():
    prediction = run_prediction("6")

    assert prediction.explanation
    assert isinstance(prediction.explanation, str)

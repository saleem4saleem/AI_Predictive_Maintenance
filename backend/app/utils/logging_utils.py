from __future__ import annotations

import logging


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_prediction_start(asset_id: str) -> None:
    get_logger("prediction").info("Prediction started for asset_id=%s", asset_id)


def log_prediction_end(asset_id: str, risk_level: str) -> None:
    get_logger("prediction").info("Prediction completed for asset_id=%s risk_level=%s", asset_id, risk_level)


def log_llm_unavailable(reason: str) -> None:
    get_logger("llm").info("LLM unavailable: %s", reason)


def log_llm_fallback_used(reason: str) -> None:
    get_logger("llm").warning("LLM fallback used: %s", reason)


def log_llm_explanation_generated(provider: str) -> None:
    get_logger("llm").info("LLM explanation generated with provider=%s", provider)


def log_llm_failure(error: Exception) -> None:
    get_logger("llm").exception("LLM explanation failed: %s", error)


def log_feedback_received(asset_id: int) -> None:
    get_logger("feedback").info("Feedback received for asset_id=%s", asset_id)


def log_feedback_saved(feedback_id: str) -> None:
    get_logger("feedback").info("Feedback saved with feedback_id=%s", feedback_id)


def log_feedback_validation_error(reason: str) -> None:
    get_logger("feedback").warning("Feedback validation error: %s", reason)


def log_feedback_storage_fallback(reason: str) -> None:
    get_logger("feedback").warning("Feedback storage fallback used: %s", reason)

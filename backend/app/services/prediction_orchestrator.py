from __future__ import annotations

from datetime import date, timedelta

from app.contracts.prediction_contract import PredictionContract
from app.services.asset_service import get_asset
from app.services.failure_mode_service import detect_failure_mode
from app.services.feature_service import build_features_for_asset, calculate_sensor_severity
from app.services.health_score_service import calculate_health_score, condition_from_health_score
from app.services.llm_service import explain_prediction
from app.services.maintenance_planning_service import get_maintenance_plan
from app.services.prediction_service import run_model_prediction
from app.services.rag_service import search_knowledge
from app.services.recommendation_service import build_recommendation
from app.services.rules_service import evaluate_rules, flatten_rule_actions, flatten_rule_causes


def run_prediction(asset_id: str) -> PredictionContract:
    asset = get_asset(asset_id)
    features = build_features_for_asset(asset.asset_id)
    model_prediction = run_model_prediction(features)
    anomaly_score = float(model_prediction.get("anomaly_score") or 0.0)
    sensor_severity = calculate_sensor_severity(features)

    rule_results = evaluate_rules(features, {"overdue_pm_days": 0})
    rule_actions = flatten_rule_actions(rule_results)
    rule_causes = flatten_rule_causes(rule_results)

    health_score = calculate_health_score(asset, anomaly_score, sensor_severity)
    condition = condition_from_health_score(health_score)
    risk_level = _combine_risk(model_prediction.get("risk_level", "low"), condition, rule_results)
    remaining_days = _estimate_remaining_useful_life_days(risk_level, health_score, anomaly_score, sensor_severity)
    predicted_failure_date = date.today() + timedelta(days=remaining_days) if remaining_days is not None else None
    failure_mode = detect_failure_mode(features, rule_causes)
    maintenance_plan = get_maintenance_plan(asset, remaining_days)
    similar = search_knowledge(f"{asset.asset_name} {failure_mode}", asset_id=asset.asset_id, limit=3)
    similar_actions = [item.summary for item in similar.results]
    recommendation = build_recommendation(
        asset,
        risk_level,
        failure_mode,
        maintenance_plan.planning_status,
        rule_actions,
        similar_actions,
    )
    top_action = recommendation["actions"][0] if recommendation["actions"] else "Continue monitoring"
    explanation = explain_prediction(asset, risk_level, failure_mode, top_action)

    return PredictionContract(
        asset_id=asset.asset_id,
        asset_code=asset.asset_code,
        asset_name=asset.asset_name,
        health_score=health_score,
        condition=condition,
        failure_probability_7_days=_failure_probability_7_days(risk_level, anomaly_score, sensor_severity),
        failure_probability_30_days=_failure_probability_30_days(risk_level, anomaly_score, sensor_severity),
        predicted_failure_date=predicted_failure_date.isoformat() if predicted_failure_date else None,
        remaining_useful_life_days=remaining_days,
        predicted_failure_mode=failure_mode,
        risk_level=risk_level,
        confidence=str(model_prediction.get("confidence", "low")),
        recommended_action=top_action,
        explanation=explanation,
        model_version=str(model_prediction.get("model_version", "unavailable")),
    )


def _combine_risk(model_risk: str, condition: str, rule_results: list[dict]) -> str:
    order = {"low": 1, "medium": 2, "high": 3, "critical": 4, "unknown": 1}
    condition_risk = {"healthy": "low", "normal": "low", "attention": "medium", "warning": "high", "critical": "critical"}
    highest = max(order.get(model_risk, 1), order[condition_risk[condition]])
    if any(result.get("severity") == "critical" for result in rule_results):
        highest = max(highest, 4)
    if any(result.get("severity") == "high" for result in rule_results):
        highest = max(highest, 3)
    return {value: key for key, value in order.items() if key != "unknown"}[highest]


def _estimate_remaining_useful_life_days(risk_level: str, health_score: float, anomaly_score: float, sensor_severity: float) -> int:
    pressure = min(1.0, anomaly_score * 0.55 + sensor_severity * 0.35 + (100 - health_score) / 100 * 0.10)
    if risk_level == "critical":
        return max(1, min(7, round(7 - pressure * 5)))
    if risk_level == "high":
        return max(7, min(30, round(30 - pressure * 18)))
    if risk_level == "medium":
        return max(30, min(90, round(90 - pressure * 45)))
    return max(90, round(120 - pressure * 20))


def _failure_probability_7_days(risk_level: str, anomaly_score: float, sensor_severity: float) -> float:
    base = {"low": 0.06, "medium": 0.18, "high": 0.42, "critical": 0.72}[risk_level]
    return round(min(0.98, base + anomaly_score * 0.12 + sensor_severity * 0.10), 3)


def _failure_probability_30_days(risk_level: str, anomaly_score: float, sensor_severity: float) -> float:
    base = {"low": 0.14, "medium": 0.38, "high": 0.68, "critical": 0.9}[risk_level]
    return round(min(0.99, base + anomaly_score * 0.12 + sensor_severity * 0.08), 3)

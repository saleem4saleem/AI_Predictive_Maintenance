from __future__ import annotations

from datetime import date, timedelta

from app.contracts.overview_contract import AssetOverviewCard, OverviewResponse, ProductionFlowAsset
from app.services.asset_service import criticality_label, list_assets


def get_factory_overview() -> OverviewResponse:
    production_flow: list[ProductionFlowAsset] = []
    cards: list[AssetOverviewCard] = []
    today = date.today()
    for index, asset in enumerate(list_assets(), start=1):
        planned_date = today + timedelta(days=14 if asset.criticality >= 95 else 21 if asset.criticality >= 85 else 30)
        predicted_failure_date = _placeholder_failure_date(asset.risk_level, today)
        production_flow.append(
            ProductionFlowAsset(
                asset_id=asset.asset_id,
                asset_code=asset.asset_code,
                asset_name=asset.asset_name,
                status=asset.status,
                health_score=asset.health_score,
                risk_level=asset.risk_level,
                predicted_failure_date=_date_or_none(predicted_failure_date),
                next_planned_maintenance=planned_date.isoformat(),
                ai_recommended_maintenance=_date_or_none(_placeholder_ai_maintenance_date(asset.risk_level, today)),
            )
        )
        cards.append(
            AssetOverviewCard(
                asset_id=asset.asset_id,
                asset_code=asset.asset_code,
                asset_name=asset.asset_name,
                asset_type=asset.asset_type,
                status=asset.status,
                health_score=asset.health_score,
                risk_level=asset.risk_level,
                criticality=criticality_label(asset.criticality),
                open_actions=1 if asset.status in {"attention", "warning", "critical"} else 0,
                predicted_failure_date=_date_or_none(predicted_failure_date),
            )
        )

    critical_assets = sum(1 for card in cards if card.risk_level in {"high", "critical"})
    open_actions = sum(1 for card in cards if card.status in {"attention", "warning", "critical"})
    factory_health = round(sum(card.health_score for card in cards) / len(cards), 1)
    weekly_downtime = round(sum(1.5 for card in cards if card.risk_level == "high") + sum(3.0 for card in cards if card.risk_level == "critical"), 1)
    return OverviewResponse(
        factory_name="Ardagh Glass Plant 1",
        factory_health=factory_health,
        critical_assets=critical_assets,
        open_actions=open_actions,
        weekly_downtime_risk_hours=weekly_downtime,
        production_flow=production_flow,
        assets=cards,
    )


def get_overview() -> OverviewResponse:
    return get_factory_overview()


def _placeholder_failure_date(risk_level: str, today: date) -> date | None:
    if risk_level == "high":
        return today + timedelta(days=18)
    if risk_level == "critical":
        return today + timedelta(days=5)
    if risk_level == "medium":
        return today + timedelta(days=45)
    return None


def _placeholder_ai_maintenance_date(risk_level: str, today: date) -> date | None:
    if risk_level == "high":
        return today + timedelta(days=10)
    if risk_level == "critical":
        return today + timedelta(days=2)
    if risk_level == "medium":
        return today + timedelta(days=21)
    return None


def _date_or_none(value: date | None) -> str | None:
    return value.isoformat() if value else None


from app.contracts.overview_contract import AssetOverviewCard, OverviewResponse, ProductionFlowAsset


def test_overview_response_can_be_created_with_flow_and_cards() -> None:
    flow_asset = ProductionFlowAsset(
        asset_id=1,
        asset_code="FURNACE_001",
        asset_name="Furnace",
        status="healthy",
        health_score=91,
        risk_level="low",
        predicted_failure_date=None,
        next_planned_maintenance="2026-06-15",
        ai_recommended_maintenance=None,
    )
    card = AssetOverviewCard(
        asset_id=1,
        asset_code="FURNACE_001",
        asset_name="Furnace",
        asset_type="Thermal Process",
        status="healthy",
        health_score=91,
        risk_level="low",
        criticality="critical",
        open_actions=0,
        predicted_failure_date=None,
    )

    response = OverviewResponse(
        factory_name="Demo Glass Factory",
        factory_health=82,
        critical_assets=2,
        open_actions=7,
        weekly_downtime_risk_hours=4.5,
        production_flow=[flow_asset],
        assets=[card],
    )

    assert response.production_flow[0].asset_code == "FURNACE_001"
    assert response.assets[0].criticality == "critical"

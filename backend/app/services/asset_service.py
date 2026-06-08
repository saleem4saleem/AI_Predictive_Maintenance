from __future__ import annotations

from app.contracts.asset_contract import AssetBasicResponse, AssetContract, AssetListResponse
from app.exceptions import ResourceNotFoundError


ASSETS: list[AssetContract] = [
    AssetContract(asset_id="1", asset_code="FURNACE_001", asset_name="Furnace", asset_type="Thermal Process", location="Hot End", status="healthy", health_score=91, risk_level="low", process_area="Hot End", criticality=98, downtime_cost_per_hour=18500, description="Continuous melting furnace and thermal control system."),
    AssetContract(asset_id="2", asset_code="FEEDER_001", asset_name="Feeder System", asset_type="Glass Delivery", location="Glass Conditioning", status="healthy", health_score=88, risk_level="low", process_area="Glass Conditioning", criticality=88, downtime_cost_per_hour=14200, description="Feeder system delivering conditioned glass to forming."),
    AssetContract(asset_id="3", asset_code="IS_MACHINE_001", asset_name="IS Forming Machine", asset_type="Forming Equipment", location="Hot End Forming", status="attention", health_score=68, risk_level="high", process_area="Hot End Forming", criticality=96, downtime_cost_per_hour=22000, description="Bottle forming machine with sections, molds, drives, and pneumatic components."),
    AssetContract(asset_id="4", asset_code="ANNEALING_LEHR_001", asset_name="Annealing Lehr", asset_type="Thermal Process", location="Annealing", status="healthy", health_score=84, risk_level="low", process_area="Annealing", criticality=82, downtime_cost_per_hour=12800, description="Thermal stress relief and cooling tunnel."),
    AssetContract(asset_id="5", asset_code="INSPECTION_001", asset_name="Inspection Machine", asset_type="Quality Equipment", location="Cold End Quality", status="attention", health_score=74, risk_level="medium", process_area="Cold End Quality", criticality=80, downtime_cost_per_hour=9800, description="Vision, camera, scanner, and rejection system."),
    AssetContract(asset_id="6", asset_code="PACKAGING_001", asset_name="Packaging Machine", asset_type="Packaging Equipment", location="Packaging", status="attention", health_score=72, risk_level="medium", process_area="Packaging", criticality=76, downtime_cost_per_hour=8600, description="Case packing, wrapping, labeling, and sealing equipment."),
    AssetContract(asset_id="7", asset_code="PALLETIZER_001", asset_name="Palletizer", asset_type="Palletizing Equipment", location="Palletizing", status="healthy", health_score=81, risk_level="low", process_area="Palletizing", criticality=74, downtime_cost_per_hour=8200, description="Layer forming, robot palletizing, and stretch wrapping system."),
    AssetContract(asset_id="8", asset_code="CONVEYOR_001", asset_name="Conveyor System", asset_type="Transport Equipment", location="Transport", status="healthy", health_score=86, risk_level="low", process_area="Transport", criticality=84, downtime_cost_per_hour=11200, description="Infeed, accumulation, transfer, and outfeed conveyors."),
]


def list_assets() -> list[AssetContract]:
    return ASSETS


def get_assets() -> list[AssetBasicResponse]:
    """Return frontend-facing asset summaries.

    The internal sample list can later be replaced with database queries without
    changing the route contract.
    """

    return [_to_asset_basic_response(asset) for asset in ASSETS]


def get_asset_list() -> AssetListResponse:
    assets = get_assets()
    return AssetListResponse(assets=assets, total=len(assets))


def get_asset_by_id(asset_id: int | str) -> AssetBasicResponse:
    return _to_asset_basic_response(get_asset(asset_id))


def get_asset(asset_id: str | int) -> AssetContract:
    normalized = str(asset_id).strip().lower()
    for asset in ASSETS:
        if normalized in {asset.asset_id.lower(), asset.asset_code.lower()}:
            return asset
    raise ResourceNotFoundError(f"Asset '{asset_id}' was not found.")


def production_flow_names() -> list[str]:
    return [asset.asset_name for asset in ASSETS]


def criticality_label(value: int) -> str:
    if value >= 95:
        return "critical"
    if value >= 85:
        return "high"
    if value >= 70:
        return "medium"
    return "low"


def _to_asset_basic_response(asset: AssetContract) -> AssetBasicResponse:
    return AssetBasicResponse(
        asset_id=int(asset.asset_id),
        asset_code=asset.asset_code,
        asset_name=asset.asset_name,
        asset_type=asset.asset_type,
        location=asset.location,
        status=asset.status,
        criticality=criticality_label(asset.criticality),
        health_score=asset.health_score,
        risk_level=asset.risk_level,
    )

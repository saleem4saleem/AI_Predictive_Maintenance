from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID, uuid4

from app.contracts.sap_notification_contracts import (
    NotificationProposal,
    SAPNotificationFormPayload,
    SAPNotificationResponse,
)
from app.core.config import PROJECT_ROOT
from app.exceptions import InvalidRequestError, ResourceNotFoundError
from app.services.asset_component_service import get_components_by_asset
from app.services.asset_service import get_asset
from app.services.prediction_service import get_prediction
from app.services.sensor_service import get_latest_sensor_values


PROPOSED = "PROPOSED"
APPROVED = "APPROVED"
REJECTED = "REJECTED"
CREATED_IN_SAP = "CREATED_IN_SAP"

PROPOSAL_STORE_PATH = PROJECT_ROOT / "data" / "sample" / "notification_proposals.json"


def generate_proposals_for_asset(asset_id: int | str) -> list[NotificationProposal]:
    """Generate AI-proposed SAP M1 notification candidates for an asset.

    The proposal logic combines current sample sensor values, the stable
    prediction response, and component metadata. Storage is currently a local
    JSON fallback so the app can run without PostgreSQL; the included migration
    documents the future database table.
    """

    asset = get_asset(asset_id)
    components = get_components_by_asset(asset.asset_id).components
    sensor_values = get_latest_sensor_values(asset.asset_id)
    prediction = get_prediction(asset.asset_id)
    existing = _load_proposals()
    created: list[NotificationProposal] = []

    for signal in _ranked_sensor_signals(sensor_values)[:2]:
        component = _select_component_for_signal(components, signal["sensor_name"])
        if component is None:
            continue

        duplicate = _find_open_duplicate(
            existing + created,
            asset_id=int(asset.asset_id),
            component_id=component.component_id,
            sensor_name=signal["sensor_name"],
        )
        if duplicate:
            created.append(duplicate)
            continue

        proposal = NotificationProposal(
            proposal_id=uuid4(),
            asset_id=int(asset.asset_id),
            component_id=component.component_id,
            asset_code=_sap_functional_location(asset.asset_code),
            asset_name=asset.asset_name,
            equipment_name=component.component_name,
            sensor_name=signal["sensor_name"],
            current_value=signal["current_value"],
            threshold=signal["threshold"],
            ai_confidence=_confidence_for(asset.risk_level, signal["severity"]),
            failure_description=_build_failure_description(
                asset_name=asset.asset_name,
                component_name=component.component_name,
                signal=signal,
                predicted_failure_mode=prediction.predicted_failure_mode,
            ),
            predicted_failure_date=_parse_prediction_date(prediction.predicted_failure_date),
            status=PROPOSED,
            created_at=_utc_now(),
        )
        created.append(proposal)

    if created:
        merged = _merge_proposals(existing, created)
        _save_proposals(merged)

    return created


def get_pending_proposals() -> list[NotificationProposal]:
    proposals = _load_proposals()
    if not proposals:
        proposals = []
        for asset_id in (3, 6):
            proposals.extend(generate_proposals_for_asset(asset_id))

    return _sort_proposals([proposal for proposal in _load_proposals() if proposal.status == PROPOSED])


def get_proposal(proposal_id: UUID | str) -> NotificationProposal:
    proposal_uuid = _to_uuid(proposal_id)
    for proposal in _load_proposals():
        if proposal.proposal_id == proposal_uuid:
            return proposal
    raise ResourceNotFoundError(f"Notification proposal '{proposal_id}' was not found.")


def approve_proposal(
    proposal_id: UUID | str,
    reviewer_name: str,
    comments: str | None = None,
) -> NotificationProposal:
    if not reviewer_name.strip():
        raise InvalidRequestError("Reviewer name is required.")

    def updater(proposal: NotificationProposal) -> NotificationProposal:
        if proposal.status not in {PROPOSED, APPROVED}:
            raise InvalidRequestError(f"Proposal cannot be approved from status '{proposal.status}'.")
        return proposal.model_copy(
            update={
                "status": APPROVED,
                "reviewed_by": reviewer_name.strip(),
                "review_comments": _clean_text(comments),
                "review_date": _utc_now(),
            }
        )

    return _update_proposal(proposal_id, updater)


def reject_proposal(
    proposal_id: UUID | str,
    reviewer_name: str,
    reason: str,
) -> NotificationProposal:
    if not reviewer_name.strip():
        raise InvalidRequestError("Reviewer name is required.")
    if not reason.strip():
        raise InvalidRequestError("Rejection reason is required.")

    def updater(proposal: NotificationProposal) -> NotificationProposal:
        if proposal.status in {CREATED_IN_SAP, REJECTED}:
            raise InvalidRequestError(f"Proposal cannot be rejected from status '{proposal.status}'.")
        return proposal.model_copy(
            update={
                "status": REJECTED,
                "reviewed_by": reviewer_name.strip(),
                "review_comments": reason.strip(),
                "review_date": _utc_now(),
            }
        )

    return _update_proposal(proposal_id, updater)


def get_sap_form_payload(proposal_id: UUID | str) -> SAPNotificationFormPayload:
    proposal = get_proposal(proposal_id)
    user_status = "Call out" if proposal.ai_confidence >= 80 else "Standard working hours"
    return SAPNotificationFormPayload(
        functional_location=proposal.asset_code,
        equipment=proposal.equipment_name,
        planner_group=proposal.asset_code,
        work_center=proposal.asset_code,
        reported_by="Saleem AI",
        description=proposal.failure_description,
        user_status=user_status,
        breakdown_duration=0.0,
        unsafepotential_risk=proposal.ai_confidence >= 90,
        proposal_id=proposal.proposal_id,
        asset_id=proposal.asset_id,
        component_id=proposal.component_id,
    )


def create_in_sap(
    proposal_id: UUID | str,
    sap_form_data: SAPNotificationFormPayload,
) -> SAPNotificationResponse:
    """Create the approved proposal in SAP.

    No SAP RFC/OData connector is configured in this repository yet, so this
    method uses a deterministic local simulator and stores the resulting
    notification number. The service boundary is ready for a real SAP adapter.
    """

    proposal = get_proposal(proposal_id)
    if proposal.status == CREATED_IN_SAP and proposal.sap_notification_number:
        return SAPNotificationResponse(
            proposal_id=proposal.proposal_id,
            status=proposal.status,
            sap_notification_number=proposal.sap_notification_number,
            message="SAP notification was already created.",
            sap_form_data=sap_form_data,
        )

    if proposal.status != APPROVED:
        raise InvalidRequestError("Proposal must be approved before SAP notification creation.")

    if sap_form_data.proposal_id != proposal.proposal_id:
        raise InvalidRequestError("SAP form payload proposal_id does not match the proposal.")

    notification_number = _generate_sap_notification_number(proposal)

    def updater(item: NotificationProposal) -> NotificationProposal:
        return item.model_copy(
            update={
                "status": CREATED_IN_SAP,
                "sap_notification_number": notification_number,
                "sap_creation_date": _utc_now(),
            }
        )

    updated = _update_proposal(proposal.proposal_id, updater)
    return SAPNotificationResponse(
        proposal_id=updated.proposal_id,
        status=updated.status,
        sap_notification_number=notification_number,
        message="SAP M1 notification created successfully in local SAP adapter simulation.",
        sap_form_data=sap_form_data,
    )


def get_proposal_history(status: str | None = None) -> list[NotificationProposal]:
    proposals = _load_proposals()
    if status:
        normalized = status.strip().upper()
        return _sort_proposals([proposal for proposal in proposals if proposal.status == normalized])
    return _sort_proposals([proposal for proposal in proposals if proposal.status != PROPOSED])


def _load_proposals() -> list[NotificationProposal]:
    if not PROPOSAL_STORE_PATH.exists():
        return []

    try:
        raw_items = json.loads(PROPOSAL_STORE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    return [NotificationProposal(**item) for item in raw_items]


def _save_proposals(proposals: list[NotificationProposal]) -> None:
    PROPOSAL_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = [proposal.model_dump(mode="json") for proposal in proposals]
    PROPOSAL_STORE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _update_proposal(
    proposal_id: UUID | str,
    updater,
) -> NotificationProposal:
    proposal_uuid = _to_uuid(proposal_id)
    proposals = _load_proposals()
    for index, proposal in enumerate(proposals):
        if proposal.proposal_id == proposal_uuid:
            updated = updater(proposal)
            proposals[index] = updated
            _save_proposals(proposals)
            return updated
    raise ResourceNotFoundError(f"Notification proposal '{proposal_id}' was not found.")


def _merge_proposals(
    existing: list[NotificationProposal],
    generated: list[NotificationProposal],
) -> list[NotificationProposal]:
    merged = list(existing)
    known_ids = {proposal.proposal_id for proposal in merged}
    for proposal in generated:
        if proposal.proposal_id not in known_ids:
            merged.append(proposal)
            known_ids.add(proposal.proposal_id)
    return merged


def _find_open_duplicate(
    proposals: list[NotificationProposal],
    *,
    asset_id: int,
    component_id: int,
    sensor_name: str,
) -> NotificationProposal | None:
    for proposal in proposals:
        if (
            proposal.asset_id == asset_id
            and proposal.component_id == component_id
            and proposal.sensor_name == sensor_name
            and proposal.status in {PROPOSED, APPROVED}
        ):
            return proposal
    return None


def _ranked_sensor_signals(values: dict[str, float]) -> list[dict[str, float | str]]:
    checks = [
        ("vibration", values.get("vibration", 0.0), 7.0, "above"),
        ("temperature", values.get("temperature", 0.0), 90.0, "above"),
        ("current_value", values.get("current_value", 0.0), 180.0, "above"),
        ("pressure", values.get("pressure", 0.0), 5.0, "below"),
        ("speed", values.get("speed", 0.0), 80.0, "below"),
        ("flow", values.get("flow", 0.0), 45.0, "below"),
    ]

    signals: list[dict[str, float | str]] = []
    for sensor_name, current_value, threshold, direction in checks:
        breached = current_value > threshold if direction == "above" else current_value < threshold
        if not breached:
            continue
        if direction == "above":
            severity = min(2.5, current_value / max(threshold, 1.0))
        else:
            severity = min(2.5, threshold / max(current_value, 0.1))
        signals.append(
            {
                "sensor_name": sensor_name,
                "current_value": float(current_value),
                "threshold": float(threshold),
                "direction": direction,
                "severity": float(severity),
            }
        )
    return sorted(signals, key=lambda item: float(item["severity"]), reverse=True)


def _select_component_for_signal(components, sensor_name: str):
    keyword_map = {
        "vibration": ["bearing", "drive", "motor", "shear", "alignment", "case packer", "pneumatic"],
        "temperature": ["temperature", "lubrication", "cooling", "heating", "burner", "seal"],
        "current_value": ["motor", "drive", "shear", "case packer", "wrap", "pneumatic"],
        "pressure": ["suction", "pneumatic", "gate", "flow", "valve"],
        "speed": ["drive", "motor", "belt", "chain", "roller", "case packer"],
        "flow": ["suction", "flow", "cooling", "lubrication", "pneumatic", "filter"],
    }
    keywords = keyword_map.get(sensor_name, [])

    for keyword in keywords:
        for component in components:
            haystack = f"{component.component_name} {component.component_code} {component.description or ''}".lower()
            if keyword in haystack:
                return component

    sensor_components = [component for component in components if component.has_sensor_data or component.has_cbm]
    return sensor_components[0] if sensor_components else (components[0] if components else None)


def _sap_functional_location(asset_code: str) -> str:
    hot_end_assets = {"FURNACE_001", "FEEDER_001", "IS_MACHINE_001", "ANNEALING_LEHR_001"}
    cold_end_assets = {"INSPECTION_001", "PACKAGING_001", "PALLETIZER_001", "CONVEYOR_001"}
    if asset_code in hot_end_assets:
        return "310"
    if asset_code in cold_end_assets:
        return "111"
    return asset_code


def _confidence_for(risk_level: str, severity: float | str) -> float:
    base = {"low": 58.0, "medium": 72.0, "high": 84.0, "critical": 92.0}.get(risk_level, 65.0)
    return min(98.0, round(base + (float(severity) - 1.0) * 8.0, 1))


def _build_failure_description(
    *,
    asset_name: str,
    component_name: str,
    signal: dict[str, float | str],
    predicted_failure_mode: str | None,
) -> str:
    sensor_name = str(signal["sensor_name"])
    current_value = float(signal["current_value"])
    threshold = float(signal["threshold"])
    direction = "exceeded" if signal["direction"] == "above" else "fell below"
    failure_mode = predicted_failure_mode or "component degradation pattern"
    return (
        f"{sensor_name.replace('_', ' ').title()} threshold {direction}: "
        f"{current_value:g} (threshold: {threshold:g}). {asset_name} component "
        f"{component_name} is showing a {failure_mode}. Review before creating the SAP M1 notification."
    )


def _parse_prediction_date(value: str | None) -> datetime | None:
    if not value:
        return _utc_now() + timedelta(days=14)
    try:
        return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
    except ValueError:
        return _utc_now() + timedelta(days=14)


def _generate_sap_notification_number(proposal: NotificationProposal) -> str:
    return f"M1{_utc_now():%y%m%d}{str(proposal.proposal_id.int)[-6:]}"


def _to_uuid(value: UUID | str) -> UUID:
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value))
    except ValueError as exc:
        raise InvalidRequestError(f"Invalid proposal id '{value}'.") from exc


def _sort_proposals(proposals: list[NotificationProposal]) -> list[NotificationProposal]:
    return sorted(proposals, key=lambda proposal: proposal.created_at, reverse=True)


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

from __future__ import annotations

import pytest

from app.services import notification_proposal_service as service


@pytest.fixture()
def notification_store(tmp_path, monkeypatch):
    store_path = tmp_path / "notification_proposals.json"
    monkeypatch.setattr(service, "PROPOSAL_STORE_PATH", store_path)
    return store_path


def test_notification_proposals_generate_from_sample_data(notification_store) -> None:
    proposals = service.get_pending_proposals()

    assert proposals
    assert all(proposal.status == service.PROPOSED for proposal in proposals)
    assert {proposal.asset_code for proposal in proposals}.issubset({"111", "310"})
    assert any(proposal.asset_id == 3 for proposal in proposals)
    assert any(proposal.asset_id == 6 for proposal in proposals)


def test_notification_proposal_approval_and_sap_payload(notification_store) -> None:
    proposal = service.get_pending_proposals()[0]

    approved = service.approve_proposal(proposal.proposal_id, "Saleem", "Create SAP notification.")
    payload = service.get_sap_form_payload(proposal.proposal_id)

    assert approved.status == service.APPROVED
    assert payload.functional_location in {"111", "310"}
    assert payload.planner_group == payload.functional_location
    assert payload.work_center == payload.functional_location
    assert payload.reported_by == "Saleem AI"
    assert payload.equipment == proposal.equipment_name


def test_notification_proposal_api_lifecycle(client, notification_store) -> None:
    pending_response = client.get("/api/v1/notification-proposals/pending")
    assert pending_response.status_code == 200
    pending = pending_response.json()
    assert pending

    proposal_id = pending[0]["proposal_id"]
    approve_response = client.post(
        f"/api/v1/notification-proposals/{proposal_id}/approve",
        json={"reviewer_name": "Maintenance Manager", "comments": "Approved after review."},
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == service.APPROVED

    form_response = client.get(f"/api/v1/notification-proposals/{proposal_id}/sap-form-data")
    assert form_response.status_code == 200
    form_data = form_response.json()
    assert form_data["functional_location"] in {"111", "310"}
    assert form_data["reported_by"] == "Saleem AI"

    create_response = client.post(
        f"/api/v1/notification-proposals/{proposal_id}/create-in-sap",
        json={"sap_form_data": form_data},
    )
    assert create_response.status_code == 200
    create_payload = create_response.json()
    assert create_payload["status"] == service.CREATED_IN_SAP
    assert create_payload["sap_notification_number"].startswith("M1")

    history_response = client.get("/api/v1/notification-proposals/history")
    assert history_response.status_code == 200
    assert any(item["proposal_id"] == proposal_id for item in history_response.json())


def test_notification_proposal_rejects_with_reason(client, notification_store) -> None:
    proposal_id = client.get("/api/v1/notification-proposals/pending").json()[0]["proposal_id"]

    response = client.post(
        f"/api/v1/notification-proposals/{proposal_id}/reject",
        json={"reviewer_name": "Maintenance Manager", "reason": "Duplicate of existing work order."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == service.REJECTED
    assert body["review_comments"] == "Duplicate of existing work order."

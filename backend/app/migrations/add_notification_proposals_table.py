from __future__ import annotations


SQL = """
CREATE TABLE IF NOT EXISTS notification_proposals (
    proposal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id INTEGER NOT NULL REFERENCES assets(asset_id),
    component_id INTEGER NOT NULL,
    asset_code VARCHAR(50) NOT NULL,
    equipment_name VARCHAR(255) NOT NULL,
    sensor_name VARCHAR(255) NOT NULL,
    current_value FLOAT NOT NULL,
    threshold FLOAT NOT NULL,
    ai_confidence FLOAT NOT NULL,
    failure_description TEXT NOT NULL,
    predicted_failure_date TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'PROPOSED',
    created_at TIMESTAMP DEFAULT NOW(),
    reviewed_by VARCHAR(255),
    review_comments TEXT,
    review_date TIMESTAMP,
    sap_notification_number VARCHAR(50),
    sap_creation_date TIMESTAMP,
    created_in_app_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_status ON notification_proposals(status);
CREATE INDEX IF NOT EXISTS idx_notifications_asset ON notification_proposals(asset_id);
"""


def get_sql() -> str:
    """Return the PostgreSQL migration SQL for deployment tooling."""

    return SQL

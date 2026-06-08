import { BrainCircuit, RadioTower } from "lucide-react";
import type { ComponentDetailResponse } from "../../types/assetComponent";
import { formatDate } from "../../utils/date";
import { formatNumber } from "../../utils/formatters";
import { Card } from "../common/Card";
import { StatusBadge } from "../common/StatusBadge";

interface ComponentDetailPanelProps {
  detail: ComponentDetailResponse | null;
  loading: boolean;
  error: string | null;
}

export function ComponentDetailPanel({ detail, loading, error }: ComponentDetailPanelProps) {
  if (loading) {
    return (
      <Card title="Selected Component Detail">
        <p className="muted">Loading component detail...</p>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Selected Component Detail">
        <p className="error-message">{error}</p>
      </Card>
    );
  }

  if (!detail) {
    return (
      <Card title="Selected Component Detail">
        <p className="muted">Select a component to inspect maintenance strategy, history, and recommendations.</p>
      </Card>
    );
  }

  const component = detail.component;
  const hasMonitoring = component.has_sensor_data || component.has_cbm;

  return (
    <Card title="Selected Component Detail" subtitle="Maintenance strategy, component health, and available condition monitoring.">
      <div className="component-detail-card standalone">
        <div className="split-row">
          <div>
            <span className="eyebrow">{component.component_code}</span>
            <h3>{component.component_name}</h3>
            <p>{component.description || component.component_type}</p>
          </div>
          <StatusBadge status={component.condition} />
        </div>

        <div className="component-detail-grid">
          <ComponentFact label="Criticality" value={component.criticality} />
          <ComponentFact label="Health" value={component.health_score === null || component.health_score === undefined ? "Not available" : `${formatNumber(component.health_score, 0)}%`} />
          <ComponentFact label="Maintenance interval" value={component.maintenance_interval_days ? `${component.maintenance_interval_days} days` : "Inspection based"} />
          <ComponentFact label="Last maintenance" value={formatDate(component.last_maintenance_date)} />
          <ComponentFact label="Next planned" value={formatDate(component.next_planned_maintenance)} />
          <ComponentFact label="CBM status" value={hasMonitoring ? "Condition monitoring available" : "No direct sensors"} />
        </div>

        <div className="component-message">
          <RadioTower size={18} />
          <p>
            {hasMonitoring
              ? "Condition monitoring available. Show sensor/CBM information for this component and compare it with maintenance history."
              : "No direct sensor data is available for this component. The recommendation is based on maintenance history, replacement interval, inspection tasks, and technician feedback."}
          </p>
        </div>

        {component.frequent_failures.length > 0 && (
          <div>
            <h4>Frequent Failures</h4>
            <div className="failure-chip-list">
              {component.frequent_failures.map((failure) => (
                <span className="badge badge-warning" key={failure}>{failure}</span>
              ))}
            </div>
          </div>
        )}

        <div className="component-message ai-learning">
          <BrainCircuit size={18} />
          <p>{detail.strategy_assessment || "AI learning status: more maintenance history and technician feedback will help optimize this maintenance interval."}</p>
        </div>
      </div>
    </Card>
  );
}

export function ComponentFact({ label, value }: { label: string; value: string }) {
  return (
    <div className="component-fact">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

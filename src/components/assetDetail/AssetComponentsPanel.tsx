import type { AssetComponent } from "../../types/assetComponent";
import { formatDate } from "../../utils/date";
import { Card } from "../common/Card";
import { EmptyState } from "../common/EmptyState";
import { RiskBadge } from "../common/RiskBadge";
import { StatusBadge } from "../common/StatusBadge";

interface AssetComponentsPanelProps {
  components: AssetComponent[];
  selectedComponentId: number | null;
  onSelectComponent: (componentId: number) => void;
}

export function AssetComponentsPanel({ components, selectedComponentId, onSelectComponent }: AssetComponentsPanelProps) {
  if (!components.length) {
    return (
      <Card title="Asset Parts & Components">
        <EmptyState title="No components available." message="Component structure will appear when SAP PM or sample component data is available." />
      </Card>
    );
  }

  return (
    <Card
      title="Asset Parts & Components"
      subtitle="Maintainable parts, maintenance strategy, condition, and component-level recommendations."
    >
      <div className="component-overview-grid" aria-label="Asset components">
        {components.map((component) => (
          <button
            className={selectedComponentId === component.component_id ? "component-card selected" : "component-card"}
            key={component.component_id}
            type="button"
            onClick={() => onSelectComponent(component.component_id)}
          >
            <div className="split-row">
              <strong>{component.component_name}</strong>
              <RiskBadge risk={component.criticality} />
            </div>
            <p>{component.component_type}</p>
            <div className="flow-badges">
              <StatusBadge status={component.condition} />
              <span className={component.has_sensor_data || component.has_cbm ? "badge badge-success" : "badge badge-unknown"}>
                {component.has_sensor_data || component.has_cbm ? "CBM available" : "No direct sensors"}
              </span>
            </div>
            <dl className="component-card-facts">
              <div>
                <dt>Strategy</dt>
                <dd>{component.maintenance_strategy}</dd>
              </div>
              <div>
                <dt>Interval</dt>
                <dd>{component.maintenance_interval_days ? `${component.maintenance_interval_days} days` : "Inspection based"}</dd>
              </div>
              <div>
                <dt>Last maintenance</dt>
                <dd>{formatDate(component.last_maintenance_date)}</dd>
              </div>
              <div>
                <dt>Next planned</dt>
                <dd>{formatDate(component.next_planned_maintenance)}</dd>
              </div>
            </dl>
            {component.frequent_failures.length > 0 && (
              <p className="component-failure-note">Frequent: {component.frequent_failures.slice(0, 2).join(", ")}</p>
            )}
            {component.recommended_action && <p className="component-card-action">{component.recommended_action}</p>}
          </button>
        ))}
      </div>
    </Card>
  );
}

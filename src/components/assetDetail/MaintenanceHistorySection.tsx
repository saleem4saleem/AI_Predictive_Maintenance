import type { AssetComponent, ComponentDetailResponse, ComponentMaintenanceHistory } from "../../types/assetComponent";
import { formatDate } from "../../utils/date";
import { formatNumber, formatValue } from "../../utils/formatters";
import { Card } from "../common/Card";
import { EmptyState } from "../common/EmptyState";

interface MaintenanceHistorySectionProps {
  detail: ComponentDetailResponse | null;
  assetHistory?: ComponentMaintenanceHistory[];
  components?: AssetComponent[];
  assetName?: string;
  loading: boolean;
}

export function MaintenanceHistorySection({ detail, assetHistory = [], components = [], assetName, loading }: MaintenanceHistorySectionProps) {
  if (loading) {
    return (
      <Card title="Past Maintenance History">
        <p className="muted">Loading maintenance history...</p>
      </Card>
    );
  }

  const history = detail?.maintenance_history || assetHistory;
  const subtitle = detail
    ? `Component-level work order history for ${detail.component.component_name}.`
    : `Asset-level work order history${assetName ? ` for ${assetName}` : ""}.`;
  const emptyTitle = detail
    ? "No past maintenance history available for this component yet."
    : "No past maintenance history available for this asset yet.";

  return (
    <Card
      title="Past Maintenance History"
      subtitle={subtitle}
    >
      {history.length === 0 ? (
        <EmptyState title={emptyTitle} message="History will appear when work orders or technician feedback are available." />
      ) : (
        <div className="table-scroll">
          <table className="maintenance-history-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Work Order</th>
                <th>Component</th>
                <th>Failure</th>
                <th>Cause</th>
                <th>Action Taken</th>
                <th>Replaced Part</th>
                <th>Downtime</th>
                <th>Technician Note</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.history_id}>
                  <td>{formatDate(item.date)}</td>
                  <td>{formatValue(item.work_order_id)}</td>
                  <td>{detail?.component.component_name || getComponentName(components, item.component_id)}</td>
                  <td>{formatValue(item.failure_description)}</td>
                  <td>{formatValue(item.failure_cause)}</td>
                  <td>{item.action_taken}</td>
                  <td>{formatValue(item.replaced_part)}</td>
                  <td>{formatNumber(item.downtime_hours, 1)} hrs</td>
                  <td>{formatValue(item.technician_note)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}

function getComponentName(components: AssetComponent[], componentId: number): string {
  return components.find((component) => component.component_id === componentId)?.component_name || `Component ${componentId}`;
}

import { Card } from "../common/Card";

export function WorkOrderPanel() {
  return (
    <Card title="Work Order Panel" subtitle="Work-order creation will connect to the backend when the endpoint is available.">
      <p className="muted">No work-order write endpoint is available yet. Maintenance recommendations are displayed as planning guidance.</p>
    </Card>
  );
}

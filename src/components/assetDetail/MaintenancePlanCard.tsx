import type { MaintenancePlanResponse } from "../../types/maintenancePlan";
import { formatDate } from "../../utils/date";
import { titleCase } from "../../utils/formatters";
import { Card } from "../common/Card";
import { RiskBadge } from "../common/RiskBadge";

export function MaintenancePlanCard({ plan }: { plan: MaintenancePlanResponse }) {
  return (
    <Card title="Planned vs Predicted Maintenance">
      <div className="timeline-compare">
        <div>
          <span>Next planned PM</span>
          <strong>{formatDate(plan.next_planned_maintenance)}</strong>
        </div>
        <div>
          <span>AI recommended date</span>
          <strong>{formatDate(plan.ai_recommended_maintenance)}</strong>
        </div>
      </div>
      <div className="card-divider" />
      <div className="split-row">
        <RiskBadge risk={plan.priority} />
        <strong>{titleCase(plan.recommendation)}</strong>
      </div>
      <p className="muted">{plan.reason}</p>
    </Card>
  );
}

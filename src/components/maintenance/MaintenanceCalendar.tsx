import type { MaintenancePlanResponse } from "../../types/maintenancePlan";
import { formatDate } from "../../utils/date";
import { Card } from "../common/Card";

export function MaintenanceCalendar({ plan }: { plan: MaintenancePlanResponse }) {
  return (
    <Card title="Maintenance Calendar">
      <div className="calendar-strip">
        <div>
          <span>Planned</span>
          <strong>{formatDate(plan.next_planned_maintenance)}</strong>
        </div>
        <div>
          <span>AI Recommended</span>
          <strong>{formatDate(plan.ai_recommended_maintenance)}</strong>
        </div>
        <div>
          <span>Open Work Orders</span>
          <strong>{plan.open_work_orders ?? "Not available"}</strong>
        </div>
      </div>
    </Card>
  );
}

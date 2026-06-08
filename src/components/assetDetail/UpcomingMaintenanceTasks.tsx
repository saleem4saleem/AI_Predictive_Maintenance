import type { MaintenancePlanResponse } from "../../types/maintenancePlan";
import type { AssetComponent, ComponentDetailResponse, ComponentUpcomingTask } from "../../types/assetComponent";
import { formatDate } from "../../utils/date";
import { titleCase } from "../../utils/formatters";
import { Card } from "../common/Card";
import { EmptyState } from "../common/EmptyState";
import { RiskBadge } from "../common/RiskBadge";

interface UpcomingMaintenanceTasksProps {
  plan: MaintenancePlanResponse;
  components: AssetComponent[];
  selectedDetail: ComponentDetailResponse | null;
  assetTasks?: ComponentUpcomingTask[];
}

export function UpcomingMaintenanceTasks({ plan, components, selectedDetail, assetTasks = [] }: UpcomingMaintenanceTasksProps) {
  const selectedTasks = selectedDetail?.upcoming_tasks || [];
  const visibleAssetTasks = selectedDetail ? [] : assetTasks.slice(0, 8);
  const componentTasks = components
    .filter((component) => component.next_planned_maintenance)
    .slice()
    .sort((a, b) => String(a.next_planned_maintenance).localeCompare(String(b.next_planned_maintenance)))
    .slice(0, 6);

  return (
    <Card title="Coming Maintenance Tasks" subtitle="Planned maintenance dates, component strategy, and AI timing advice.">
      <div className="task-list">
        <div className="task-row maintenance-task-row">
          <div>
            <strong>{titleCase(plan.recommendation)}</strong>
            <p>{plan.reason}</p>
            <span>Asset-level plan - Next planned {formatDate(plan.next_planned_maintenance)}</span>
          </div>
          <RiskBadge risk={plan.priority} />
          <strong>{formatDate(plan.ai_recommended_maintenance)}</strong>
        </div>

        {selectedTasks.map((task) => (
          <ScheduledTaskRow task={task} componentName={selectedDetail?.component.component_name} key={task.schedule_id} />
        ))}

        {visibleAssetTasks.map((task) => (
          <ScheduledTaskRow task={task} componentName={getComponentName(components, task.component_id)} key={task.schedule_id} />
        ))}

        {selectedDetail && selectedTasks.length === 0 && (
          <div className="task-row maintenance-task-row">
            <div>
              <strong>{selectedDetail.component.recommended_action || `Inspect ${selectedDetail.component.component_name}`}</strong>
              <p>{selectedDetail.component.maintenance_strategy}</p>
              <span>
                Selected component - Interval {selectedDetail.component.maintenance_interval_days ? `${selectedDetail.component.maintenance_interval_days} days` : "inspection based"}
              </span>
            </div>
            <RiskBadge risk={selectedDetail.component.criticality} />
            <strong>{formatDate(selectedDetail.component.next_planned_maintenance)}</strong>
          </div>
        )}

        {!selectedDetail && visibleAssetTasks.length === 0 && componentTasks.map((component) => (
          <div className="task-row maintenance-task-row" key={component.component_id}>
            <div>
              <strong>{component.component_name}</strong>
              <p>{component.recommended_action || component.maintenance_strategy}</p>
              <span>{component.has_sensor_data || component.has_cbm ? "Condition based task" : "Strategy/history based task"}</span>
            </div>
            <RiskBadge risk={component.criticality} />
            <strong>{formatDate(component.next_planned_maintenance)}</strong>
          </div>
        ))}
      </div>

      {componentTasks.length === 0 && visibleAssetTasks.length === 0 && !selectedDetail && (
        <EmptyState title="No upcoming maintenance tasks available." message="Component dates will appear when SAP PM plans or sample schedules are available." />
      )}
      {selectedDetail && selectedTasks.length === 0 && !selectedDetail.component.next_planned_maintenance && (
        <EmptyState title="No upcoming maintenance tasks available for this component yet." message="Tasks will appear when sample schedules, SAP PM plans, or planner updates are available." />
      )}
    </Card>
  );
}

function getComponentName(components: AssetComponent[], componentId?: number | null): string | undefined {
  if (!componentId) return undefined;
  return components.find((component) => component.component_id === componentId)?.component_name;
}

function ScheduledTaskRow({ task, componentName }: { task: ComponentUpcomingTask; componentName?: string }) {
  return (
    <div className="task-row maintenance-task-row detailed-task-row">
      <div>
        <strong>{task.task_name}</strong>
        <p>{task.ai_reason || task.maintenance_strategy || "Planned component maintenance task."}</p>
        <dl className="task-detail-grid">
          <div>
            <dt>Component</dt>
            <dd>{componentName || task.component_code || "Asset-level"}</dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>{titleCase(task.status)}</dd>
          </div>
          <div>
            <dt>Strategy</dt>
            <dd>{task.maintenance_strategy || "Not available"}</dd>
          </div>
          <div>
            <dt>Last completed</dt>
            <dd>{formatDate(task.last_completed_date)}</dd>
          </div>
          <div>
            <dt>Interval</dt>
            <dd>{task.recommended_interval_days ? `${task.recommended_interval_days} days` : task.frequency || "Inspection based"}</dd>
          </div>
          <div>
            <dt>AI date</dt>
            <dd>{formatDate(task.ai_recommended_date)}</dd>
          </div>
        </dl>
      </div>
      <RiskBadge risk={task.priority} />
      <strong>{formatDate(task.planned_date)}</strong>
    </div>
  );
}

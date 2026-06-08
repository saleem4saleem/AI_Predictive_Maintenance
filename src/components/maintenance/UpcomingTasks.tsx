import type { RecommendationItem } from "../../types/recommendation";
import { formatDate } from "../../utils/date";
import { Card } from "../common/Card";
import { RiskBadge } from "../common/RiskBadge";

export function UpcomingTasks({ tasks }: { tasks: RecommendationItem[] }) {
  return (
    <Card title="Upcoming Tasks">
      <div className="task-list">
        {tasks.map((task, index) => (
          <div className="task-row" key={`${task.action}-${index}`}>
            <div>
              <strong>{task.action}</strong>
              <p>{task.reason || "No reason supplied."}</p>
            </div>
            <span>{formatDate(task.due_date)}</span>
            <RiskBadge risk={task.priority} />
          </div>
        ))}
      </div>
    </Card>
  );
}

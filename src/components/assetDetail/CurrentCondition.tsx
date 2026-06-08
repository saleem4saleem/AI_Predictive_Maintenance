import type { CurrentCondition as CurrentConditionType } from "../../types/asset";
import { formatDateTime } from "../../utils/date";
import { titleCase } from "../../utils/formatters";
import { Card } from "../common/Card";
import { StatusBadge } from "../common/StatusBadge";
import { HealthScoreGauge } from "./HealthScoreGauge";

export function CurrentCondition({ condition }: { condition: CurrentConditionType }) {
  return (
    <Card title="Current Condition">
      <div className="condition-layout">
        <HealthScoreGauge score={condition.health_score} />
        <div className="condition-facts">
          <StatusBadge status={condition.condition} />
          <p>Trend: {titleCase(condition.trend || "unknown")}</p>
          <p>Last update: {formatDateTime(condition.last_updated)}</p>
        </div>
      </div>
    </Card>
  );
}

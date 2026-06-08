import { CheckCircle2 } from "lucide-react";
import type { RecommendationItem } from "../../types/recommendation";
import { formatDate } from "../../utils/date";
import { Card } from "../common/Card";
import { RiskBadge } from "../common/RiskBadge";

export function RecommendedActions({ actions }: { actions: RecommendationItem[] }) {
  return (
    <Card title="Recommended Actions">
      <div className="action-list">
        {actions.map((item, index) => (
          <div className="action-item" key={`${item.action}-${index}`}>
            <CheckCircle2 size={18} />
            <div>
              <strong>{item.action}</strong>
              <p>{item.reason || "No reason supplied."}</p>
              <span>Due: {formatDate(item.due_date)} · Source: {item.source || "backend"}</span>
            </div>
            <RiskBadge risk={item.priority} />
          </div>
        ))}
      </div>
    </Card>
  );
}

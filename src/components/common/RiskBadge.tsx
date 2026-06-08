import { titleCase } from "../../utils/formatters";
import { statusClass } from "../../utils/status";

interface RiskBadgeProps {
  risk?: string | null;
}

export function RiskBadge({ risk }: RiskBadgeProps) {
  return <span className={`badge badge-${statusClass(risk)}`}>{titleCase(risk || "unknown")} Risk</span>;
}

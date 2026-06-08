import { titleCase } from "../../utils/formatters";
import { statusClass } from "../../utils/status";

interface StatusBadgeProps {
  status?: string | null;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return <span className={`badge badge-${statusClass(status)}`}>{titleCase(status || "unknown")}</span>;
}

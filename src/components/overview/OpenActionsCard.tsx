import { ClipboardList } from "lucide-react";
import { MetricCard } from "../common/MetricCard";

export function OpenActionsCard({ value }: { value: number }) {
  return <MetricCard icon={ClipboardList} label="Open Actions" value={String(value)} note="Maintenance actions open" tone="amber" />;
}

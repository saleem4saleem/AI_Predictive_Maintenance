import { Clock3 } from "lucide-react";
import { MetricCard } from "../common/MetricCard";

export function DowntimeRiskCard({ value }: { value: number }) {
  return <MetricCard icon={Clock3} label="Weekly Downtime Risk" value={`${value.toFixed(1)} hrs`} note="Predicted risk window" tone="blue" />;
}

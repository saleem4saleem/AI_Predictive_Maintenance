import { OctagonAlert } from "lucide-react";
import { MetricCard } from "../common/MetricCard";

export function CriticalAssetsCard({ value }: { value: number }) {
  return <MetricCard icon={OctagonAlert} label="Critical Assets" value={String(value)} note="Assets requiring attention" tone="red" />;
}

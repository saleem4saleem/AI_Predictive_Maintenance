import { ShieldCheck } from "lucide-react";
import { MetricCard } from "../common/MetricCard";

export function FactoryHealthCard({ value }: { value: number }) {
  return <MetricCard icon={ShieldCheck} label="Factory Health" value={`${value.toFixed(0)}%`} note="Backend overview snapshot" tone="green" />;
}

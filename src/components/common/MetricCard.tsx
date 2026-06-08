import type { LucideIcon } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string;
  note?: string;
  icon: LucideIcon;
  tone?: "blue" | "green" | "amber" | "red";
}

export function MetricCard({ label, value, note, icon: Icon, tone = "blue" }: MetricCardProps) {
  return (
    <section className={`metric-card metric-${tone}`}>
      <div className="metric-icon">
        <Icon size={24} />
      </div>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
        {note && <span>{note}</span>}
      </div>
    </section>
  );
}

import { Activity, Gauge, Thermometer, Zap } from "lucide-react";
import type { SensorSummary } from "../../types/asset";
import { formatNumber } from "../../utils/formatters";
import { MetricCard } from "../common/MetricCard";

export function SensorSummaryCards({ sensors }: { sensors: SensorSummary }) {
  return (
    <div className="sensor-grid">
      <MetricCard icon={Activity} label="Vibration" value={formatNumber(sensors.vibration, 1)} note="mm/s" tone="blue" />
      <MetricCard icon={Thermometer} label="Temperature" value={formatNumber(sensors.temperature, 1)} note="deg C" tone="amber" />
      <MetricCard icon={Gauge} label="Pressure" value={formatNumber(sensors.pressure, 1)} note="bar" tone="green" />
      <MetricCard icon={Zap} label="Current" value={formatNumber(sensors.current_value, 1)} note="A" tone="red" />
    </div>
  );
}

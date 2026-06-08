import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { SensorHistoryPoint } from "../../types/sensor";

export function SensorMultiChart({ data }: { data: SensorHistoryPoint[] }) {
  return (
    <div className="chart-box">
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e6edf5" />
          <XAxis dataKey="timestamp" hide />
          <YAxis />
          <Tooltip />
          <Line dataKey="vibration" stroke="#0f6bff" strokeWidth={2} dot={false} />
          <Line dataKey="temperature" stroke="#f59e0b" strokeWidth={2} dot={false} />
          <Line dataKey="pressure" stroke="#10b981" strokeWidth={2} dot={false} />
          <Line dataKey="current_value" stroke="#ef4444" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

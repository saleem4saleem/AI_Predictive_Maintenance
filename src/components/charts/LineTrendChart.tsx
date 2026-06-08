import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface LineTrendChartProps<T extends Record<string, unknown>> {
  data: T[];
  dataKey: string;
  color?: string;
}

export function LineTrendChart<T extends Record<string, unknown>>({ data, dataKey, color = "#0f6bff" }: LineTrendChartProps<T>) {
  return (
    <div className="chart-box">
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e6edf5" />
          <XAxis dataKey="timestamp" hide />
          <YAxis />
          <Tooltip />
          <Line dataKey={dataKey} stroke={color} strokeWidth={2.5} dot={false} type="monotone" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

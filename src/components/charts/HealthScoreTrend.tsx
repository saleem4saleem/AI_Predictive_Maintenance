import { LineTrendChart } from "./LineTrendChart";

export function HealthScoreTrend({ data }: { data: Array<{ timestamp: string; health_score: number }> }) {
  return <LineTrendChart data={data} dataKey="health_score" color="#10b981" />;
}

import { LineTrendChart } from "./LineTrendChart";

export function FailureRiskTrend({ data }: { data: Array<{ timestamp: string; risk: number }> }) {
  return <LineTrendChart data={data} dataKey="risk" color="#ef4444" />;
}

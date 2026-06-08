export function statusClass(status: string | null | undefined): string {
  const normalized = (status || "unknown").toLowerCase();
  if (normalized.includes("healthy") || normalized === "normal" || normalized === "low") return "success";
  if (normalized.includes("attention") || normalized === "medium") return "attention";
  if (normalized.includes("warning") || normalized === "high") return "warning";
  if (normalized.includes("critical") || normalized === "urgent") return "critical";
  return "unknown";
}

export function riskSortValue(risk: string | null | undefined): number {
  const order: Record<string, number> = { critical: 4, high: 3, medium: 2, low: 1 };
  return order[(risk || "").toLowerCase()] || 0;
}

export function healthClass(score: number | null | undefined): string {
  if (score === null || score === undefined) return "unknown";
  if (score >= 80) return "success";
  if (score >= 65) return "attention";
  if (score >= 45) return "warning";
  return "critical";
}

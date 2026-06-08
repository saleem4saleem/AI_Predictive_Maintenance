export function formatPercent(value: number | null | undefined, digits = 0): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "Not available";
  const normalized = value <= 1 ? value * 100 : value;
  return `${normalized.toFixed(digits)}%`;
}

export function formatNumber(value: number | null | undefined, digits = 0): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "Not available";
  return value.toFixed(digits);
}

export function formatValue(value: unknown, fallback = "Not available"): string {
  if (value === null || value === undefined || value === "") return fallback;
  return String(value);
}

export function titleCase(value: string | null | undefined): string {
  if (!value) return "Unknown";
  return value
    .replace(/[_-]/g, " ")
    .split(" ")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

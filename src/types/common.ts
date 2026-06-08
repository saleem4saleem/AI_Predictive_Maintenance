export type RiskLevel = "low" | "medium" | "high" | "critical" | "unknown";
export type AssetStatus = "healthy" | "attention" | "warning" | "critical" | "unknown" | string;

export interface HealthResponse {
  success: boolean;
  message: string;
  timestamp: string;
  data: {
    status?: string;
    component?: string;
    ok?: boolean;
    detail?: string;
    components?: Array<Record<string, unknown>>;
    [key: string]: unknown;
  };
}

export interface ApiErrorShape {
  message: string;
  status?: number;
}

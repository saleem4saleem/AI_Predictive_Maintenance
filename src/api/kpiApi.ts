import { apiClient } from "./client";
import type { AssetKPIResponse, FactoryKPIResponse, KPITrendPoint } from "../types/kpi";

const now = new Date().toISOString();

const assetKpiFallbacks: Record<number, AssetKPIResponse> = {
  1: fallbackAssetKpi(1, "FURNACE_001", "Furnace", 0.8, 620, 2.6, 1, 97.2, 0, 91, 84, null, 0, "2026-05-27"),
  2: fallbackAssetKpi(2, "FEEDER_001", "Feeder System", 0.6, 510, 1.9, 1, 96.8, 1, 89, 82, null, 0, "2026-05-24"),
  3: fallbackAssetKpi(3, "IS_MACHINE_001", "IS Forming Machines", 2.2, 260, 2.8, 3, 90.1, 3, 81, 75, "2026-05-04", 2, "2026-06-03"),
  4: fallbackAssetKpi(4, "ANNEALING_LEHR_001", "Annealing Lehr", 0.7, 480, 2.3, 1, 95.6, 0, 90, 80, null, 0, "2026-05-28"),
  5: fallbackAssetKpi(5, "INSPECTION_001", "Inspection Machines", 1.0, 390, 1.7, 2, 93.7, 2, 86, 79, "2026-04-26", 1, "2026-05-28"),
  6: fallbackAssetKpi(6, "PACKAGING_001", "Packaging Machine", 1.5, 310, 1.8, 2, 92.4, 3, 84, 78, "2026-05-08", 2, "2026-06-15"),
};

const fallbackFactoryKpis: FactoryKPIResponse = {
  factory_name: "Ardagh Glass Plant 1",
  period_label: "Last 30 days",
  downtime_hours: 6.3,
  mtbf_hours: 420,
  mttr_hours: 2.1,
  failure_count: 4,
  availability_percent: 94.8,
  open_actions: 18,
  maintenance_compliance_percent: 87,
  prediction_accuracy_percent: 82,
  critical_assets: 3,
  factory_health_score: 86,
  warning_assets: 2,
  normal_assets: 3,
  repeat_failures: 5,
  planned_maintenance_ratio_percent: 68,
  reactive_maintenance_ratio_percent: 32,
  sap_documentation_capture_rate_percent: 76,
  updated_at: now,
};

const fallbackTrend: KPITrendPoint[] = [
  { period: "Week 1", downtime_hours: 7.4, mtbf_hours: 360, mttr_hours: 2.7, availability_percent: 92.9 },
  { period: "Week 2", downtime_hours: 6.8, mtbf_hours: 382, mttr_hours: 2.4, availability_percent: 93.5 },
  { period: "Week 3", downtime_hours: 5.9, mtbf_hours: 414, mttr_hours: 2.2, availability_percent: 94.4 },
  { period: "Week 4", downtime_hours: 6.3, mtbf_hours: 420, mttr_hours: 2.1, availability_percent: 94.8 },
];

export async function getFactoryKpis(): Promise<FactoryKPIResponse> {
  try {
    const { data } = await apiClient.get<FactoryKPIResponse>("/kpis");
    return data;
  } catch {
    return fallbackFactoryKpis;
  }
}

export async function getAssetKpis(assetId: number): Promise<AssetKPIResponse> {
  try {
    const { data } = await apiClient.get<AssetKPIResponse>(`/kpis/assets/${assetId}`);
    return data;
  } catch {
    return assetKpiFallbacks[assetId] ?? fallbackAssetKpi(assetId, `ASSET_${assetId}`, "Selected Asset", 1.2, 340, 2.0, 1, 93.4, 1, 85, 76, null, 0, null);
  }
}

export async function getKpiTrends(assetId?: number): Promise<KPITrendPoint[]> {
  try {
    const endpoint = assetId ? `/kpis/assets/${assetId}/trends` : "/kpis/trends";
    const { data } = await apiClient.get<KPITrendPoint[]>(endpoint);
    return Array.isArray(data) ? data : fallbackTrend;
  } catch {
    return fallbackTrend.map((point, index) => ({
      ...point,
      downtime_hours: assetId ? Math.max(0.4, point.downtime_hours * (0.18 + index * 0.025)) : point.downtime_hours,
      mtbf_hours: assetId ? point.mtbf_hours * 0.78 : point.mtbf_hours,
      mttr_hours: assetId ? Math.max(1.1, point.mttr_hours * 0.82) : point.mttr_hours,
      availability_percent: assetId ? Math.max(88, point.availability_percent - 1.4 + index * 0.2) : point.availability_percent,
    }));
  }
}

function fallbackAssetKpi(
  asset_id: number,
  asset_code: string,
  asset_name: string,
  downtime_hours: number,
  mtbf_hours: number,
  mttr_hours: number,
  failure_count: number,
  availability_percent: number,
  open_actions: number,
  maintenance_compliance_percent: number,
  prediction_accuracy_percent: number,
  last_failure_date: string | null,
  repeat_failures: number,
  next_maintenance_date: string | null,
): AssetKPIResponse {
  return {
    asset_id,
    asset_code,
    asset_name,
    period_label: "Last 30 days",
    downtime_hours,
    mtbf_hours,
    mttr_hours,
    failure_count,
    availability_percent,
    open_actions,
    maintenance_compliance_percent,
    prediction_accuracy_percent,
    last_failure_date,
    repeat_failures,
    next_maintenance_date,
    updated_at: now,
  };
}

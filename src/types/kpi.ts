export interface FactoryKPIResponse {
  factory_name: string;
  period_label: string;
  downtime_hours: number;
  mtbf_hours: number;
  mttr_hours: number;
  failure_count: number;
  availability_percent: number;
  open_actions: number;
  maintenance_compliance_percent: number;
  prediction_accuracy_percent?: number | null;
  critical_assets: number;
  factory_health_score?: number | null;
  warning_assets?: number | null;
  normal_assets?: number | null;
  repeat_failures?: number | null;
  planned_maintenance_ratio_percent?: number | null;
  reactive_maintenance_ratio_percent?: number | null;
  sap_documentation_capture_rate_percent?: number | null;
  updated_at?: string | null;
}

export interface AssetKPIResponse {
  asset_id: number;
  asset_code: string;
  asset_name: string;
  period_label: string;
  downtime_hours: number;
  mtbf_hours: number;
  mttr_hours: number;
  failure_count: number;
  availability_percent: number;
  open_actions: number;
  maintenance_compliance_percent: number;
  prediction_accuracy_percent?: number | null;
  last_failure_date?: string | null;
  repeat_failures?: number | null;
  next_maintenance_date?: string | null;
  updated_at?: string | null;
}

export interface KPITrendPoint {
  period: string;
  downtime_hours: number;
  mtbf_hours: number;
  mttr_hours: number;
  availability_percent: number;
}

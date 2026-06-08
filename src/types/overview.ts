export interface ProductionFlowAsset {
  asset_id: number;
  asset_code: string;
  asset_name: string;
  status: string;
  health_score: number;
  risk_level: string;
  predicted_failure_date: string | null;
  next_planned_maintenance: string | null;
  ai_recommended_maintenance: string | null;
}

export interface AssetOverviewCard {
  asset_id: number;
  asset_code: string;
  asset_name: string;
  asset_type: string;
  status: string;
  health_score: number;
  risk_level: string;
  criticality: string;
  open_actions: number;
  predicted_failure_date: string | null;
}

export interface OverviewResponse {
  factory_name: string;
  factory_health: number;
  critical_assets: number;
  open_actions: number;
  weekly_downtime_risk_hours: number;
  production_flow: ProductionFlowAsset[];
  assets: AssetOverviewCard[];
}

export interface PredictionResponse {
  asset_id: number;
  asset_code: string;
  asset_name: string;
  health_score: number;
  condition: string;
  failure_probability_7_days: number;
  failure_probability_30_days: number;
  predicted_failure_date: string | null;
  remaining_useful_life_days: number | null;
  predicted_failure_mode: string | null;
  risk_level: string;
  confidence: string;
  recommended_action: string;
  explanation: string;
  model_version: string;
  generated_at?: string | null;
  data_quality?: string | null;
  warnings?: string[];
}

export interface PredictionRunRequest {
  asset_id: number;
}

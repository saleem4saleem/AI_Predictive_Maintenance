import type { MaintenancePlanResponse } from "./maintenancePlan";
import type { PredictionResponse } from "./prediction";
import type { RagSearchResult } from "./rag";
import type { RecommendationItem } from "./recommendation";
import type { AssetComponent, ComponentMaintenanceHistory, ComponentUpcomingTask } from "./assetComponent";

export interface AssetBasicResponse {
  asset_id: number;
  asset_code: string;
  asset_name: string;
  asset_type: string;
  location: string | null;
  status: string;
  criticality: string;
  health_score?: number | null;
  risk_level?: string | null;
}

export interface CurrentCondition {
  health_score: number;
  condition: string;
  trend: string | null;
  last_updated: string | null;
}

export interface SensorSummary {
  timestamp: string | null;
  vibration: number | null;
  temperature: number | null;
  pressure: number | null;
  current_value: number | null;
  speed: number | null;
  flow: number | null;
  runtime_hours?: number | null;
}

export interface AIExplanation {
  summary: string;
  confidence: string;
  fallback_used: boolean;
}

export interface FeedbackStatus {
  feedback_required: boolean;
  last_feedback_at: string | null;
}

export interface AssetDetailResponse {
  asset: AssetBasicResponse;
  current_condition: CurrentCondition;
  sensor_summary: SensorSummary;
  prediction: PredictionResponse;
  maintenance_plan: MaintenancePlanResponse;
  recommended_actions: RecommendationItem[];
  similar_failures: RagSearchResult[];
  ai_explanation: AIExplanation;
  feedback_status: FeedbackStatus;
  components?: AssetComponent[];
  asset_maintenance_history?: ComponentMaintenanceHistory[];
  asset_upcoming_tasks?: ComponentUpcomingTask[];
}

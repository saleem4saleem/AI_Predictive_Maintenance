export interface MaintenancePlanResponse {
  asset_id: number;
  next_planned_maintenance: string | null;
  ai_recommended_maintenance: string | null;
  recommendation: string;
  priority: string;
  reason: string;
  planned_vs_predicted_status: string;
  next_planned_maintenance_date?: string | null;
  preventive_interval_days?: number | null;
  open_work_orders?: number | null;
  ai_recommended_date?: string | null;
  planning_status?: string | null;
  timing_advice?: string | null;
}

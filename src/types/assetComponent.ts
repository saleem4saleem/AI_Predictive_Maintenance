export interface AssetComponent {
  component_id: number;
  asset_id: number;
  component_code: string;
  component_name: string;
  component_type: string;
  description?: string | null;
  criticality: string;
  condition: string;
  health_score?: number | null;
  has_sensor_data: boolean;
  has_cbm: boolean;
  maintenance_strategy: string;
  maintenance_interval_days?: number | null;
  last_maintenance_date?: string | null;
  next_planned_maintenance?: string | null;
  frequent_failures: string[];
  recommended_action?: string | null;
}

export interface ComponentMaintenanceHistory {
  history_id: number;
  component_id: number;
  date: string;
  work_order_id?: string | null;
  failure_description?: string | null;
  failure_cause?: string | null;
  action_taken: string;
  replaced_part?: string | null;
  downtime_hours?: number | null;
  technician_note?: string | null;
}

export interface ComponentUpcomingTask {
  schedule_id: number;
  component_id?: number | null;
  asset_id: number;
  component_code?: string | null;
  task_name: string;
  planned_date: string;
  frequency?: string | null;
  last_completed_date?: string | null;
  recommended_interval_days?: number | null;
  priority: string;
  status: string;
  maintenance_strategy?: string | null;
  ai_recommended_date?: string | null;
  ai_reason?: string | null;
}

export interface AssetComponentsResponse {
  asset_id: number;
  components: AssetComponent[];
}

export interface ComponentDetailResponse {
  component: AssetComponent;
  maintenance_history: ComponentMaintenanceHistory[];
  upcoming_tasks: ComponentUpcomingTask[];
  frequent_failures: string[];
  ai_recommendation: string;
  sensor_summary?: Record<string, unknown> | null;
  strategy_assessment?: string | null;
}

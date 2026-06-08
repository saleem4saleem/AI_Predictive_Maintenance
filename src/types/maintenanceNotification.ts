export type MaintenanceNotificationPriority = "low" | "medium" | "high" | "critical";
export type MaintenanceNotificationSource =
  | "manual"
  | "ai_recommendation"
  | "condition_monitoring"
  | "predictive_maintenance"
  | "component_history";
export type MaintenanceNotificationStatus =
  | "local_test"
  | "ready_for_sap"
  | "sap_login_required"
  | "sap_portal_unreachable"
  | "sap_creation_pending_manual_step"
  | "sap_not_configured"
  | "sent_to_sap"
  | "sap_failed";

export interface MaintenanceNotificationCreateRequest {
  asset_id: number;
  asset_code?: string | null;
  asset_name?: string | null;
  component_id?: number | null;
  component_code?: string | null;
  component_name?: string | null;
  notification_type?: string;
  priority: MaintenanceNotificationPriority;
  short_text: string;
  description: string;
  failure_mode?: string | null;
  suspected_cause?: string | null;
  recommended_action?: string | null;
  source: MaintenanceNotificationSource;
  requested_by?: string | null;
}

export type MaintenanceNotificationDraft = Partial<MaintenanceNotificationCreateRequest>;

export interface MaintenanceNotification extends MaintenanceNotificationCreateRequest {
  notification_id: string;
  notification_type: string;
  status: MaintenanceNotificationStatus;
  sap_notification_number?: string | null;
  sap_confirmation_note?: string | null;
  created_at: string;
  updated_at?: string | null;
  message: string;
}

export interface MaintenanceNotificationListResponse {
  notifications: MaintenanceNotification[];
  total: number;
}

export interface SAPIntegrationStatus {
  enabled: boolean;
  configured: boolean;
  portal_url?: string | null;
  reachable: boolean;
  status: string;
  message: string;
}

export interface SAPManualConfirmationRequest {
  sap_notification_number: string;
  note?: string | null;
}

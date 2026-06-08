export type NotificationProposalStatus = "PROPOSED" | "APPROVED" | "REJECTED" | "CREATED_IN_SAP";

export interface NotificationProposal {
  proposal_id: string;
  asset_id: number;
  component_id: number;
  asset_code: string;
  asset_name: string;
  equipment_name: string;
  sensor_name: string;
  current_value: number;
  threshold: number;
  ai_confidence: number;
  failure_description: string;
  predicted_failure_date?: string | null;
  status: NotificationProposalStatus;
  created_at: string;
  reviewed_by?: string | null;
  review_comments?: string | null;
  review_date?: string | null;
  sap_notification_number?: string | null;
  sap_creation_date?: string | null;
}

export interface SAPNotificationFormPayload {
  functional_location: string;
  equipment: string;
  planner_group: string;
  work_center: string;
  reported_by: string;
  description: string;
  user_status: "Call out" | "Standard working hours" | string;
  breakdown_duration: number;
  unsafepotential_risk: boolean;
  proposal_id: string;
  asset_id: number;
  component_id: number;
}

export interface SAPNotificationResponse {
  proposal_id: string;
  status: NotificationProposalStatus;
  sap_notification_number: string;
  message: string;
  sap_form_data: SAPNotificationFormPayload;
}

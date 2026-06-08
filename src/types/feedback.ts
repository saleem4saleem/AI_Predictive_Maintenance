export interface FeedbackRequest {
  asset_id: number;
  prediction_id?: number | null;
  was_prediction_correct?: boolean | null;
  actual_failure_happened?: boolean | null;
  actual_failure_mode?: string | null;
  action_taken?: string | null;
  timing_feedback?: "too_early" | "correct" | "too_late" | "not_applicable" | null;
  technician_comment?: string | null;
}

export interface FeedbackResponse {
  status: string;
  message: string;
  asset_id: number;
  feedback_id?: string | null;
  received_at?: string | null;
}

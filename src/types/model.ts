export interface ActiveModelResponse {
  model_type: string;
  version: string;
  status: string;
  trained_at: string | null;
  features: string[];
  target_type?: string | null;
  model_file_exists?: boolean | null;
  scaler_file_exists?: boolean | null;
  component?: string | null;
  ok?: boolean | null;
  detail?: string | null;
  model_version?: string | null;
  metrics?: Record<string, unknown> | null;
}

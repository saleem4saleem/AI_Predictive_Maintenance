export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}

export interface AIChatRequest {
  message: string;
  asset_id?: number | null;
  context?: Record<string, unknown> | null;
}

export interface AIChatResponse {
  answer: string;
  confidence?: "low" | "medium" | "high" | string;
  fallback_used: boolean;
  suggestions?: string[];
}

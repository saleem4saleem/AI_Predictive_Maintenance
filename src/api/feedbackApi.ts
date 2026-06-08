import { apiClient } from "./client";
import type { FeedbackRequest, FeedbackResponse } from "../types/feedback";

export async function submitFeedback(payload: FeedbackRequest): Promise<FeedbackResponse> {
  const { data } = await apiClient.post<FeedbackResponse>("/feedback", payload);
  return data;
}

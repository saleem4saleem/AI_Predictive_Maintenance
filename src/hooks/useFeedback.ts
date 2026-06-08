import { useState } from "react";
import { submitFeedback } from "../api/feedbackApi";
import { toApiError } from "../api/client";
import type { FeedbackRequest, FeedbackResponse } from "../types/feedback";

export function useFeedback() {
  const [data, setData] = useState<FeedbackResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(payload: FeedbackRequest) {
    setLoading(true);
    setError(null);
    try {
      const result = await submitFeedback(payload);
      setData(result);
      return result;
    } catch (err) {
      setError(toApiError(err).message);
      return null;
    } finally {
      setLoading(false);
    }
  }

  return { data, loading, error, submit };
}

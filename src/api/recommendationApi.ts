import { apiClient } from "./client";
import type { RecommendationResponse } from "../types/recommendation";

export async function getRecommendations(assetId: number | string): Promise<RecommendationResponse> {
  const { data } = await apiClient.get<RecommendationResponse>(`/recommendations/${assetId}`);
  return data;
}

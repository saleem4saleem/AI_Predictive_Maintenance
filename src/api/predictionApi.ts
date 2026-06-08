import { apiClient } from "./client";
import type { PredictionResponse } from "../types/prediction";

export async function getPrediction(assetId: number | string): Promise<PredictionResponse> {
  const { data } = await apiClient.get<PredictionResponse>(`/predictions/${assetId}`);
  return data;
}

export async function runPrediction(assetId: number | string): Promise<PredictionResponse> {
  const { data } = await apiClient.post<PredictionResponse>("/predictions/run", {
    asset_id: Number(assetId),
  });
  return data;
}

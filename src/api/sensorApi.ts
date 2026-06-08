import { apiClient } from "./client";
import type { SensorHistoryResponse, SensorLatestResponse } from "../types/sensor";

export async function getLatestSensors(assetId: number | string): Promise<SensorLatestResponse> {
  const { data } = await apiClient.get<SensorLatestResponse>(`/sensors/${assetId}`);
  return data;
}

export async function getSensorHistory(assetId: number | string, limit = 24): Promise<SensorHistoryResponse> {
  const { data } = await apiClient.get<SensorHistoryResponse>(`/sensors/${assetId}/history`, {
    params: { limit },
  });
  return data;
}

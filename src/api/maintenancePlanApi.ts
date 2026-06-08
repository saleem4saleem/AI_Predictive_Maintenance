import { apiClient } from "./client";
import type { MaintenancePlanResponse } from "../types/maintenancePlan";

export async function getMaintenancePlan(assetId: number | string): Promise<MaintenancePlanResponse> {
  const { data } = await apiClient.get<MaintenancePlanResponse>(`/maintenance-plans/${assetId}`);
  return data;
}

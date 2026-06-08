import { apiClient } from "./client";
import type { OverviewResponse } from "../types/overview";

export async function getFactoryOverview(): Promise<OverviewResponse> {
  const { data } = await apiClient.get<OverviewResponse>("/overview");
  return data;
}

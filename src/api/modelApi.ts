import { apiClient } from "./client";
import type { ActiveModelResponse } from "../types/model";

export async function getActiveModel(): Promise<ActiveModelResponse> {
  const { data } = await apiClient.get<ActiveModelResponse>("/models/active");
  return data;
}

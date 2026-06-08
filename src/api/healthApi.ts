import { apiClient } from "./client";
import type { HealthResponse } from "../types/common";

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await apiClient.get<HealthResponse>("/health");
  return data;
}

export async function getDatabaseHealth(): Promise<HealthResponse> {
  const { data } = await apiClient.get<HealthResponse>("/health/database");
  return data;
}

export async function getModelHealth(): Promise<HealthResponse> {
  const { data } = await apiClient.get<HealthResponse>("/health/model");
  return data;
}

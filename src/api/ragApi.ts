import { apiClient } from "./client";
import type { RagSearchResponse } from "../types/rag";

export async function searchKnowledge(
  query: string,
  assetId?: number | null,
  limit = 5,
): Promise<RagSearchResponse> {
  const { data } = await apiClient.post<RagSearchResponse>("/rag/search", {
    query,
    asset_id: assetId ?? null,
    limit,
  });
  return data;
}

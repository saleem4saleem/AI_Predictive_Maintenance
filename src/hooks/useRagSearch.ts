import { useState } from "react";
import { searchKnowledge } from "../api/ragApi";
import { toApiError } from "../api/client";
import type { RagSearchResponse } from "../types/rag";

export function useRagSearch() {
  const [data, setData] = useState<RagSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function search(query: string, assetId?: number | null) {
    setLoading(true);
    setError(null);
    try {
      const result = await searchKnowledge(query, assetId);
      setData(result);
      return result;
    } catch (err) {
      setError(toApiError(err).message);
      return null;
    } finally {
      setLoading(false);
    }
  }

  return { data, loading, error, search };
}

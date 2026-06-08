export interface RagSearchRequest {
  query: string;
  asset_id?: number | null;
  limit?: number;
}

export interface RagSearchResult {
  source_type: string;
  title: string;
  summary: string;
  score: number | null;
}

export interface RagSearchResponse {
  query: string;
  results: RagSearchResult[];
}

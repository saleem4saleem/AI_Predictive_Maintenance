export interface RecommendationItem {
  action: string;
  priority: string;
  reason: string | null;
  due_date: string | null;
  source: string | null;
}

export interface RecommendationResponse {
  asset_id: number;
  recommendations: RecommendationItem[];
  actions?: string[];
  priority?: string | null;
  reason?: string | null;
}

import { getRecommendations } from "../api/recommendationApi";
import { useAsyncData } from "./useAsyncData";

export function useRecommendations(assetId: number | string) {
  return useAsyncData(() => getRecommendations(assetId), [assetId]);
}

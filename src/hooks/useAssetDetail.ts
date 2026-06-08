import { getAssetDetail } from "../api/assetApi";
import { useAsyncData } from "./useAsyncData";

export function useAssetDetail(assetId: number | string) {
  return useAsyncData(() => getAssetDetail(assetId), [assetId]);
}

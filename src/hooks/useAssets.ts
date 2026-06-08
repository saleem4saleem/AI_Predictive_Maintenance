import { getAsset, getAssets } from "../api/assetApi";
import { useAsyncData } from "./useAsyncData";

export function useAssets() {
  return useAsyncData(getAssets, []);
}

export function useAsset(assetId: number | string) {
  return useAsyncData(() => getAsset(assetId), [assetId]);
}

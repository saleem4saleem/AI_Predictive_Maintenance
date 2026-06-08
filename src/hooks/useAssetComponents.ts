import { getAssetComponentDetail, getAssetComponents } from "../api/assetApi";
import { useAsyncData } from "./useAsyncData";

export function useAssetComponents(assetId: number | string) {
  return useAsyncData(() => getAssetComponents(assetId), [assetId]);
}

export function useAssetComponentDetail(assetId: number | string, componentId: number | string) {
  return useAsyncData(() => getAssetComponentDetail(assetId, componentId), [assetId, componentId]);
}

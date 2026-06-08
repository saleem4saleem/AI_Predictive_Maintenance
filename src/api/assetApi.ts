import { apiClient, toApiError } from "./client";
import { getFallbackAssetComponents, getFallbackComponentDetail } from "./assetComponentFallback";
import type { AssetBasicResponse, AssetDetailResponse } from "../types/asset";
import type { AssetComponentsResponse, ComponentDetailResponse } from "../types/assetComponent";

export async function getAssets(): Promise<AssetBasicResponse[]> {
  const { data } = await apiClient.get<AssetBasicResponse[]>("/assets");
  return data;
}

export async function getAsset(assetId: number | string): Promise<AssetBasicResponse> {
  const { data } = await apiClient.get<AssetBasicResponse>(`/assets/${assetId}`);
  return data;
}

export async function getAssetDetail(assetId: number | string): Promise<AssetDetailResponse> {
  const { data } = await apiClient.get<AssetDetailResponse>(`/assets/${assetId}/detail`);
  return data;
}

export async function getAssetComponents(assetId: number | string): Promise<AssetComponentsResponse> {
  try {
    const { data } = await apiClient.get<AssetComponentsResponse>(`/assets/${assetId}/components`);
    return data;
  } catch (error) {
    const apiError = toApiError(error);
    const fallback = apiError.status === 404 ? getFallbackAssetComponents(assetId) : null;
    if (fallback) return fallback;
    throw error;
  }
}

export async function getAssetComponentDetail(
  assetId: number | string,
  componentId: number | string,
): Promise<ComponentDetailResponse> {
  try {
    const { data } = await apiClient.get<ComponentDetailResponse>(`/assets/${assetId}/components/${componentId}`);
    return data;
  } catch (error) {
    const apiError = toApiError(error);
    const fallback = apiError.status === 404 ? getFallbackComponentDetail(assetId, componentId) : null;
    if (fallback) return fallback;
    throw error;
  }
}

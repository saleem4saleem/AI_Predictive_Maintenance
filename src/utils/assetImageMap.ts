import type { AssetBasicResponse } from "../types/asset";
import type { AssetOverviewCard, ProductionFlowAsset } from "../types/overview";

const machineIconModules = import.meta.glob("../assets/machine-icons/*.png", {
  eager: true,
  import: "default",
  query: "?url",
}) as Record<string, string>;

type AssetLike = {
  asset_code: string;
  asset_name: string;
};

export const visibleProductionAssetCodes = [
  "FURNACE_001",
  "FEEDER_001",
  "IS_MACHINE_001",
  "ANNEALING_LEHR_001",
  "INSPECTION_001",
  "PACKAGING_001",
] as const;

const assetVisualsByCode: Record<string, { fileName: string; displayName: string; fallbackLabel: string }> = {
  FURNACE_001: {
    fileName: "furnace.png",
    displayName: "Furnace",
    fallbackLabel: "F",
  },
  FEEDER_001: {
    fileName: "feeder-system.png",
    displayName: "Feeder System",
    fallbackLabel: "FS",
  },
  IS_MACHINE_001: {
    fileName: "is-forming-machines.png",
    displayName: "IS Forming Machines",
    fallbackLabel: "IS",
  },
  ANNEALING_LEHR_001: {
    fileName: "annealing-lehr.png",
    displayName: "Annealing Lehr",
    fallbackLabel: "AL",
  },
  INSPECTION_001: {
    fileName: "inspection-machines.png",
    displayName: "Inspection Machines",
    fallbackLabel: "IM",
  },
  PACKAGING_001: {
    fileName: "packaging-machine.png",
    displayName: "Packaging Machine",
    fallbackLabel: "PM",
  },
};

export function isVisibleProductionAsset(asset: AssetLike): boolean {
  return visibleProductionAssetCodes.includes(asset.asset_code as (typeof visibleProductionAssetCodes)[number]);
}

export function filterVisibleProductionAssets<T extends AssetLike>(assets: T[]): T[] {
  return assets
    .filter(isVisibleProductionAsset)
    .sort((left, right) => getProductionAssetOrder(left.asset_code) - getProductionAssetOrder(right.asset_code));
}

export function getProductionAssetOrder(assetCode: string): number {
  const index = visibleProductionAssetCodes.indexOf(assetCode as (typeof visibleProductionAssetCodes)[number]);
  return index === -1 ? Number.MAX_SAFE_INTEGER : index + 1;
}

export function getProductionAssetDisplayName(asset: AssetLike): string {
  return assetVisualsByCode[asset.asset_code]?.displayName ?? asset.asset_name;
}

export function getAssetIllustrationUrl(assetCode: string): string | null {
  const fileName = assetVisualsByCode[assetCode]?.fileName;
  if (!fileName) {
    return null;
  }

  return machineIconModules[`../assets/machine-icons/${fileName}`] ?? null;
}

export function getAssetIllustrationFallback(asset: AssetLike): string {
  return assetVisualsByCode[asset.asset_code]?.fallbackLabel ?? getAssetInitials(asset.asset_name);
}

function getAssetInitials(assetName: string): string {
  return assetName
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();
}

export type VisibleProductionFlowAsset = ProductionFlowAsset;
export type VisibleAssetOverviewCard = AssetOverviewCard;
export type VisibleAssetBasicResponse = AssetBasicResponse;

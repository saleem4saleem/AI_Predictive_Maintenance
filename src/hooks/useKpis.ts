import { getAssetKpis, getFactoryKpis, getKpiTrends } from "../api/kpiApi";
import { useAsyncData } from "./useAsyncData";

export function useKpis(assetId?: number | null) {
  return useAsyncData(async () => {
    const [factory, asset, trends] = await Promise.all([
      getFactoryKpis(),
      assetId ? getAssetKpis(assetId) : Promise.resolve(null),
      getKpiTrends(assetId ?? undefined),
    ]);

    return { factory, asset, trends };
  }, [assetId]);
}

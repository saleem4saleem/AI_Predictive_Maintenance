import { getMaintenancePlan } from "../api/maintenancePlanApi";
import { useAsyncData } from "./useAsyncData";

export function useMaintenancePlan(assetId: number | string) {
  return useAsyncData(() => getMaintenancePlan(assetId), [assetId]);
}

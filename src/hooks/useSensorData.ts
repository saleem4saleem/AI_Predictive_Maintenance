import { getLatestSensors, getSensorHistory } from "../api/sensorApi";
import { useAsyncData } from "./useAsyncData";

export function useSensorData(assetId: number | string, limit = 24) {
  return useAsyncData(async () => {
    const [latest, history] = await Promise.all([
      getLatestSensors(assetId),
      getSensorHistory(assetId, limit),
    ]);
    return { latest, history };
  }, [assetId, limit]);
}

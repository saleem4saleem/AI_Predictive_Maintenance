import { useState } from "react";
import { getPrediction, runPrediction } from "../api/predictionApi";
import { toApiError } from "../api/client";
import type { PredictionResponse } from "../types/prediction";
import { useAsyncData } from "./useAsyncData";

export function usePrediction(assetId: number | string) {
  const state = useAsyncData(() => getPrediction(assetId), [assetId]);
  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);
  const [latestRun, setLatestRun] = useState<PredictionResponse | null>(null);

  async function run() {
    setRunning(true);
    setRunError(null);
    try {
      const result = await runPrediction(assetId);
      setLatestRun(result);
      return result;
    } catch (err) {
      setRunError(toApiError(err).message);
      return null;
    } finally {
      setRunning(false);
    }
  }

  return { ...state, data: latestRun ?? state.data, run, running, runError };
}

import { getDatabaseHealth, getHealth, getModelHealth } from "../api/healthApi";
import { useAsyncData } from "./useAsyncData";

export function useHealthCheck() {
  return useAsyncData(async () => {
    const [health, database, model] = await Promise.all([
      getHealth(),
      getDatabaseHealth(),
      getModelHealth(),
    ]);
    return { health, database, model };
  }, []);
}

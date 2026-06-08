import { getFactoryOverview } from "../api/overviewApi";
import { useAsyncData } from "./useAsyncData";

export function useFactoryOverview() {
  return useAsyncData(getFactoryOverview, []);
}

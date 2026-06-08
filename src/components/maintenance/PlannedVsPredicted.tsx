import type { MaintenancePlanResponse } from "../../types/maintenancePlan";
import { MaintenancePlanCard } from "../assetDetail/MaintenancePlanCard";

export function PlannedVsPredicted({ plan }: { plan: MaintenancePlanResponse }) {
  return <MaintenancePlanCard plan={plan} />;
}

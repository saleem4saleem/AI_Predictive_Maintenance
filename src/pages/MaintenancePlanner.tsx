import { MaintenanceCalendar } from "../components/maintenance/MaintenanceCalendar";
import { PlannedVsPredicted } from "../components/maintenance/PlannedVsPredicted";
import { UpcomingTasks } from "../components/maintenance/UpcomingTasks";
import { WorkOrderPanel } from "../components/maintenance/WorkOrderPanel";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingSkeleton } from "../components/common/LoadingSkeleton";
import { PageHeader } from "../components/layout/PageHeader";
import { useMaintenancePlan } from "../hooks/useMaintenancePlan";
import { useRecommendations } from "../hooks/useRecommendations";

export function MaintenancePlanner({ assetId }: { assetId: number }) {
  const plan = useMaintenancePlan(assetId);
  const recommendations = useRecommendations(assetId);

  if (plan.loading || recommendations.loading) return <LoadingSkeleton rows={7} />;
  if (plan.error || !plan.data) return <ErrorState message={plan.error || "Prediction is temporarily unavailable."} onRetry={plan.refresh} />;

  return (
    <div className="page-stack">
      <PageHeader title="Maintenance Planner" description="Planned maintenance compared with AI-recommended maintenance timing." />
      <div className="detail-grid">
        <PlannedVsPredicted plan={plan.data} />
        <MaintenanceCalendar plan={plan.data} />
      </div>
      {recommendations.data && <UpcomingTasks tasks={recommendations.data.recommendations} />}
      <WorkOrderPanel />
    </div>
  );
}

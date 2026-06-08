import { BellRing, RefreshCw } from "lucide-react";
import { FailurePredictionCard } from "../components/assetDetail/FailurePredictionCard";
import { Card } from "../components/common/Card";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingSkeleton } from "../components/common/LoadingSkeleton";
import { PageHeader } from "../components/layout/PageHeader";
import { usePrediction } from "../hooks/usePrediction";
import type { MaintenanceNotificationDraft } from "../types/maintenanceNotification";

export function PredictiveMaintenance({
  assetId,
  onCreateNotification,
}: {
  assetId: number;
  onCreateNotification?: (draft: MaintenanceNotificationDraft) => void;
}) {
  const { data, loading, error, refresh, run, running, runError } = usePrediction(assetId);

  if (loading) return <LoadingSkeleton rows={6} />;
  if (error || !data) return <ErrorState message={error || "Prediction is temporarily unavailable."} onRetry={refresh} />;

  return (
    <div className="page-stack">
      <PageHeader
        title="Predictive Maintenance"
        description="Prediction output is supplied by the backend; the UI only displays stable contract fields."
        actions={
          <button className="primary-button" type="button" onClick={() => void run()} disabled={running}>
            <RefreshCw size={16} /> {running ? "Running..." : "Run Prediction"}
          </button>
        }
      />
      {runError && <p className="error-message">{runError}</p>}
      <FailurePredictionCard prediction={data} />
      <Card title="Recommended Action">
        <p className="large-text">{data.recommended_action}</p>
        <p className="muted">{data.explanation}</p>
        <button
          className="primary-button"
          type="button"
          onClick={() =>
            onCreateNotification?.({
              asset_id: data.asset_id,
              asset_code: data.asset_code,
              asset_name: data.asset_name,
              priority: data.risk_level === "critical" ? "critical" : data.risk_level === "high" ? "high" : "medium",
              short_text: data.predicted_failure_mode
                ? `${data.asset_name}: ${data.predicted_failure_mode}`
                : `${data.asset_name} predictive maintenance review`,
              description: data.explanation,
              failure_mode: data.predicted_failure_mode,
              recommended_action: data.recommended_action,
              source: "predictive_maintenance",
              requested_by: "maintenance_manager",
            })
          }
        >
          <BellRing size={16} /> Create Notification
        </button>
      </Card>
    </div>
  );
}

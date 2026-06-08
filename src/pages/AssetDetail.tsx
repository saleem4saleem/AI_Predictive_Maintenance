import { BellRing } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { getAssetComponentDetail } from "../api/assetApi";
import { AssetAIRecommendation } from "../components/assetDetail/AssetAIRecommendation";
import { AssetHeader } from "../components/assetDetail/AssetHeader";
import { CurrentCondition } from "../components/assetDetail/CurrentCondition";
import { FailurePredictionCard } from "../components/assetDetail/FailurePredictionCard";
import { FeedbackPanel } from "../components/assetDetail/FeedbackPanel";
import { ComponentDetailPanel } from "../components/assetDetail/ComponentDetailPanel";
import { MaintenanceHistorySection } from "../components/assetDetail/MaintenanceHistorySection";
import { SensorSummaryCards } from "../components/assetDetail/SensorSummaryCards";
import { SimilarFailures } from "../components/assetDetail/SimilarFailures";
import { AssetComponentsPanel } from "../components/assetDetail/AssetComponentsPanel";
import { UpcomingMaintenanceTasks } from "../components/assetDetail/UpcomingMaintenanceTasks";
import { Card } from "../components/common/Card";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingSkeleton } from "../components/common/LoadingSkeleton";
import { useAssetDetail } from "../hooks/useAssetDetail";
import type { AssetComponent, ComponentDetailResponse } from "../types/assetComponent";
import type { MaintenanceNotificationDraft } from "../types/maintenanceNotification";
import { formatDate } from "../utils/date";

export function AssetDetail({
  assetId,
  onCreateNotification,
}: {
  assetId: number;
  onCreateNotification?: (draft: MaintenanceNotificationDraft) => void;
}) {
  const { data, loading, error, refresh } = useAssetDetail(assetId);
  const components = useMemo(() => data?.components || [], [data?.components]);
  const [selectedComponentId, setSelectedComponentId] = useState<number | null>(null);
  const [componentDetail, setComponentDetail] = useState<ComponentDetailResponse | null>(null);
  const [componentLoading, setComponentLoading] = useState(false);
  const [componentError, setComponentError] = useState<string | null>(null);

  useEffect(() => {
    setSelectedComponentId(null);
    setComponentDetail(null);
  }, [assetId]);

  useEffect(() => {
    if (!selectedComponentId || !data) {
      setComponentDetail(null);
      return;
    }

    const fallbackComponent = components.find((component) => component.component_id === selectedComponentId);
    let cancelled = false;
    setComponentLoading(true);
    setComponentError(null);

    getAssetComponentDetail(data.asset.asset_id, selectedComponentId)
      .then((detail) => {
        if (!cancelled) setComponentDetail(detail);
      })
      .catch(() => {
        if (!cancelled && fallbackComponent) {
          setComponentDetail(buildFallbackComponentDetail(fallbackComponent));
          setComponentError(null);
        }
      })
      .finally(() => {
        if (!cancelled) setComponentLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [data, components, selectedComponentId]);

  if (loading) return <LoadingSkeleton rows={9} />;
  if (error || !data) return <ErrorState message={error || "Prediction is temporarily unavailable."} onRetry={refresh} />;

  return (
    <div className="page-stack">
      <AssetHeader asset={data.asset} />

      <AssetComponentsPanel
        components={components}
        selectedComponentId={selectedComponentId}
        onSelectComponent={setSelectedComponentId}
      />

      <ComponentDetailPanel detail={componentDetail} loading={componentLoading} error={componentError} />
      <MaintenanceHistorySection
        detail={componentDetail}
        assetHistory={data.asset_maintenance_history}
        components={components}
        assetName={data.asset.asset_name}
        loading={componentLoading}
      />
      <UpcomingMaintenanceTasks
        plan={data.maintenance_plan}
        components={components}
        selectedDetail={componentDetail}
        assetTasks={data.asset_upcoming_tasks}
      />
      <AssetAIRecommendation
        prediction={data.prediction}
        explanation={data.ai_explanation}
        actions={data.recommended_actions}
        selectedDetail={componentDetail}
      />
      <Card
        title="Maintenance Notification"
        subtitle="Create a local SAP-ready test notification from the current asset or selected component context."
        action={
          <button
            className="primary-button"
            type="button"
            onClick={() =>
              onCreateNotification?.({
                asset_id: data.asset.asset_id,
                asset_code: data.asset.asset_code,
                asset_name: data.asset.asset_name,
                component_id: componentDetail?.component.component_id,
                component_code: componentDetail?.component.component_code,
                component_name: componentDetail?.component.component_name,
                priority: data.prediction.risk_level === "critical" ? "critical" : data.prediction.risk_level === "high" ? "high" : "medium",
                short_text: componentDetail
                  ? `${componentDetail.component.component_name} requires maintenance review`
                  : `${data.asset.asset_name} predictive maintenance review`,
                description:
                  componentDetail?.ai_recommendation ||
                  data.ai_explanation.summary ||
                  data.prediction.explanation,
                failure_mode:
                  componentDetail?.frequent_failures?.[0] ||
                  data.prediction.predicted_failure_mode,
                suspected_cause: componentDetail?.frequent_failures?.[0],
                recommended_action:
                  componentDetail?.component.recommended_action ||
                  data.prediction.recommended_action,
                source: componentDetail ? "component_history" : "ai_recommendation",
                requested_by: "maintenance_manager",
              })
            }
          >
            <BellRing size={16} /> Create Notification
          </button>
        }
      >
        <p className="muted">
          This creates a local test record only. It does not send a notification to SAP.
        </p>
      </Card>
      <ConditionMonitoringSection
        selectedComponent={componentDetail?.component || null}
        sensors={data.sensor_summary}
        condition={data.current_condition}
        prediction={data.prediction}
      />
      <SimilarFailures failures={data.similar_failures} />
      <FeedbackPanel assetId={data.asset.asset_id} />
    </div>
  );
}

function ConditionMonitoringSection({
  selectedComponent,
  sensors,
  condition,
  prediction,
}: {
  selectedComponent: AssetComponent | null;
  sensors: Parameters<typeof SensorSummaryCards>[0]["sensors"];
  condition: Parameters<typeof CurrentCondition>[0]["condition"];
  prediction: Parameters<typeof FailurePredictionCard>[0]["prediction"];
}) {
  const hasComponentMonitoring = selectedComponent ? selectedComponent.has_sensor_data || selectedComponent.has_cbm : true;

  return (
    <Card title="Sensor / Condition Monitoring" subtitle="Shown only when the selected component has direct sensors or CBM data.">
      {hasComponentMonitoring ? (
        <div className="page-stack">
          <SensorSummaryCards sensors={sensors} />
          <div className="detail-grid">
            <CurrentCondition condition={condition} />
            <FailurePredictionCard prediction={prediction} />
          </div>
        </div>
      ) : (
        <div className="no-sensor-panel">
          <strong>No direct sensor data available for {selectedComponent?.component_name}.</strong>
          <p>
            This component is managed through maintenance strategy, replacement interval, inspection results,
            failure history, and technician feedback. Sensor cards are intentionally hidden so the UI does not
            imply pressure, flow, vibration, or temperature readings exist for this part.
          </p>
          <dl className="component-detail-grid">
            <div className="component-fact">
              <span>Maintenance strategy</span>
              <strong>{selectedComponent?.maintenance_strategy || "Not available"}</strong>
            </div>
            <div className="component-fact">
              <span>Replacement / inspection interval</span>
              <strong>{selectedComponent?.maintenance_interval_days ? `${selectedComponent.maintenance_interval_days} days` : "Inspection based"}</strong>
            </div>
            <div className="component-fact">
              <span>Last maintenance</span>
              <strong>{formatDate(selectedComponent?.last_maintenance_date)}</strong>
            </div>
            <div className="component-fact">
              <span>Next planned</span>
              <strong>{formatDate(selectedComponent?.next_planned_maintenance)}</strong>
            </div>
          </dl>
        </div>
      )}
    </Card>
  );
}

function buildFallbackComponentDetail(component: AssetComponent): ComponentDetailResponse {
  return {
    component,
    maintenance_history: [],
    upcoming_tasks: [],
    frequent_failures: component.frequent_failures,
    ai_recommendation:
      component.recommended_action ||
      "AI learning status: more maintenance history and technician feedback will help optimize this maintenance interval.",
    sensor_summary: null,
    strategy_assessment:
      "AI learning status: more maintenance history and technician feedback will help optimize this maintenance interval.",
  };
}

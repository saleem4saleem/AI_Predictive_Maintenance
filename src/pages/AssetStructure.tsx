import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Boxes, CheckCircle2, Factory, RadioTower, Wrench } from "lucide-react";
import { getAssetComponentDetail } from "../api/assetApi";
import { Card } from "../components/common/Card";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingSkeleton } from "../components/common/LoadingSkeleton";
import { PageHeader } from "../components/layout/PageHeader";
import { useAssetComponents } from "../hooks/useAssetComponents";
import type { AssetBasicResponse } from "../types/asset";
import type { AssetComponent, ComponentDetailResponse } from "../types/assetComponent";
import { formatDate } from "../utils/date";
import { formatNumber } from "../utils/formatters";
import { filterVisibleProductionAssets, getProductionAssetDisplayName } from "../utils/assetImageMap";
import { RiskBadge } from "../components/common/RiskBadge";
import { StatusBadge } from "../components/common/StatusBadge";

interface AssetStructureProps {
  assetId: number;
  assets: AssetBasicResponse[];
  onSelectAsset: (assetId: number) => void;
  onOpenAssetDetail: () => void;
}

export function AssetStructure({ assetId, assets, onSelectAsset, onOpenAssetDetail }: AssetStructureProps) {
  const visibleAssets = filterVisibleProductionAssets(assets);
  const selectedAsset = visibleAssets.find((asset) => asset.asset_id === assetId) || visibleAssets[0];
  const selectedAssetId = selectedAsset?.asset_id || assetId;
  const componentsState = useAssetComponents(selectedAssetId);
  const components = componentsState.data?.components || [];
  const [selectedComponentId, setSelectedComponentId] = useState<number | null>(null);
  const [componentDetail, setComponentDetail] = useState<ComponentDetailResponse | null>(null);
  const [componentLoading, setComponentLoading] = useState(false);
  const [componentError, setComponentError] = useState<string | null>(null);

  useEffect(() => {
    setSelectedComponentId(null);
    setComponentDetail(null);
  }, [selectedAssetId]);

  useEffect(() => {
    if (!selectedComponentId) {
      setComponentDetail(null);
      return;
    }

    let cancelled = false;
    setComponentLoading(true);
    setComponentError(null);
    getAssetComponentDetail(selectedAssetId, selectedComponentId)
      .then((detail) => {
        if (!cancelled) setComponentDetail(detail);
      })
      .catch((error) => {
        if (!cancelled) setComponentError(error instanceof Error ? error.message : "Component detail is unavailable.");
      })
      .finally(() => {
        if (!cancelled) setComponentLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [selectedAssetId, selectedComponentId]);

  const stats = useMemo(() => buildStats(components), [components]);
  const frequentFailures = useMemo(
    () => Array.from(new Set(components.flatMap((component) => component.frequent_failures))).slice(0, 8),
    [components],
  );

  if (!visibleAssets.length) {
    return <ErrorState message="Backend is not reachable. Please check the API server." />;
  }

  return (
    <div className="page-stack asset-structure-page">
      <PageHeader
        title="Asset Structure"
        description="SAP-style asset hierarchy, components, maintenance strategy, and maintainable items."
        actions={
          <button className="primary-button" type="button" onClick={onOpenAssetDetail}>
            Open Asset Detail
          </button>
        }
      />

      <Card title="Production Asset Flow" subtitle="Factory -> Area -> Asset -> Component -> Maintainable Item -> Work Orders">
        <div className="structure-flow" aria-label="Production asset sequence">
          {visibleAssets.map((asset, index) => (
            <div className="structure-flow-step" key={asset.asset_id}>
              <button
                className={asset.asset_id === selectedAssetId ? "structure-asset-card selected" : "structure-asset-card"}
                type="button"
                onClick={() => onSelectAsset(asset.asset_id)}
              >
                <span className="structure-order">{index + 1}</span>
                <strong>{getProductionAssetDisplayName(asset)}</strong>
                <small>{asset.asset_code}</small>
                <div className="flow-badges">
                  <StatusBadge status={asset.status} />
                  <RiskBadge risk={asset.criticality} />
                </div>
                <div className="structure-health-line">
                  <span style={{ width: `${Math.min(100, asset.health_score || 0)}%` }} />
                </div>
                <dl>
                  <div>
                    <dt>Health</dt>
                    <dd>{formatNumber(asset.health_score, 0)}%</dd>
                  </div>
                  <div>
                    <dt>Type</dt>
                    <dd>{asset.asset_type}</dd>
                  </div>
                </dl>
              </button>
              {index < visibleAssets.length - 1 && <ArrowRight className="structure-flow-arrow" size={22} />}
            </div>
          ))}
        </div>
      </Card>

      <div className="asset-structure-layout">
        <section className="page-stack">
          <SelectedAssetSummary
            asset={selectedAsset}
            stats={stats}
            frequentFailures={frequentFailures}
            onOpenAssetDetail={onOpenAssetDetail}
          />

          <Card
            title="Components of Selected Asset"
            subtitle="Maintainable components and parts loaded from backend component endpoints."
          >
            {componentsState.loading ? (
              <LoadingSkeleton rows={4} />
            ) : componentsState.error ? (
              <ErrorState
                title={componentsState.error.toLowerCase().includes("not found") ? "Component endpoint was not found" : undefined}
                message={
                  componentsState.error.toLowerCase().includes("not found")
                    ? `Component endpoint was not found. Check /api/v1/assets/${selectedAssetId}/components.`
                    : componentsState.error
                }
                onRetry={componentsState.refresh}
              />
            ) : components.length ? (
              <div className="structure-component-table">
                {components.map((component) => (
                  <button
                    className={selectedComponentId === component.component_id ? "structure-component-row selected" : "structure-component-row"}
                    key={component.component_id}
                    type="button"
                    onClick={() => setSelectedComponentId(component.component_id)}
                  >
                    <div>
                      <strong>{component.component_name}</strong>
                      <span>{component.component_code} - {component.component_type}</span>
                    </div>
                    <StatusBadge status={component.condition} />
                    <RiskBadge risk={component.criticality} />
                    <span>{component.health_score === null || component.health_score === undefined ? "No score" : `${formatNumber(component.health_score, 0)}%`}</span>
                    <span className={component.has_sensor_data || component.has_cbm ? "badge badge-success" : "badge badge-unknown"}>
                      {component.has_sensor_data || component.has_cbm ? "CBM available" : "No direct sensors"}
                    </span>
                    <span>{component.maintenance_interval_days ? `${component.maintenance_interval_days} days` : "Inspection based"}</span>
                    <span>{formatDate(component.next_planned_maintenance)}</span>
                  </button>
                ))}
              </div>
            ) : (
              <EmptyState title="No components available." message="Component structure will appear when backend sample data or SAP PM import data is available." />
            )}
          </Card>
        </section>

        <StructureComponentDetail
          component={components.find((item) => item.component_id === selectedComponentId) || null}
          detail={componentDetail}
          loading={componentLoading}
          error={componentError}
        />
      </div>
    </div>
  );
}

function SelectedAssetSummary({
  asset,
  stats,
  frequentFailures,
  onOpenAssetDetail,
}: {
  asset: AssetBasicResponse | undefined;
  stats: ReturnType<typeof buildStats>;
  frequentFailures: string[];
  onOpenAssetDetail: () => void;
}) {
  if (!asset) return null;

  return (
    <Card title={`${getProductionAssetDisplayName(asset)} Structure`} subtitle={`${asset.asset_code} - ${asset.location || "Factory area"}`}>
      <div className="structure-summary-grid">
        <StructureFact icon={Boxes} label="Components" value={String(stats.total)} />
        <StructureFact icon={RadioTower} label="With CBM/Sensors" value={String(stats.withSensors)} />
        <StructureFact icon={Wrench} label="Without Sensors" value={String(stats.withoutSensors)} />
        <StructureFact icon={CheckCircle2} label="Next Maintenance" value={formatDate(stats.nextMaintenance)} />
      </div>
      <div className="structure-hierarchy">
        <span>Factory</span>
        <ArrowRight size={16} />
        <span>{asset.location || "Area"}</span>
        <ArrowRight size={16} />
        <span>{getProductionAssetDisplayName(asset)}</span>
        <ArrowRight size={16} />
        <span>Components</span>
        <ArrowRight size={16} />
        <span>Work Orders</span>
      </div>
      <div className="structure-summary-split">
        <div>
          <strong>Maintenance strategy overview</strong>
          <p>
            Components are split between condition-based monitoring and strategy/history-based maintenance.
            Non-sensor components use inspection results, replacement intervals, work orders, and technician feedback.
          </p>
        </div>
        <div>
          <strong>Frequent failures summary</strong>
          <div className="failure-chip-list">
            {frequentFailures.length ? frequentFailures.map((failure) => (
              <span className="badge badge-warning" key={failure}>{failure}</span>
            )) : <span className="muted">No repeated failures captured yet.</span>}
          </div>
        </div>
      </div>
      <button className="secondary-button" type="button" onClick={onOpenAssetDetail}>
        Open Asset Detail
      </button>
    </Card>
  );
}

function StructureComponentDetail({
  component,
  detail,
  loading,
  error,
}: {
  component: AssetComponent | null;
  detail: ComponentDetailResponse | null;
  loading: boolean;
  error: string | null;
}) {
  if (loading) {
    return (
      <Card title="Component Detail">
        <p className="muted">Loading component detail...</p>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Component Detail">
        <p className="error-message">{error}</p>
      </Card>
    );
  }

  if (!component) {
    return (
      <Card title="Component Detail" subtitle="Click a component to inspect strategy, history, and upcoming work.">
        <div className="structure-empty-detail">
          <Factory size={32} />
          <p>Select a component from the table to see its SAP-style maintainable item detail.</p>
        </div>
      </Card>
    );
  }

  const hasMonitoring = component.has_sensor_data || component.has_cbm;
  const history = detail?.maintenance_history || [];
  const upcoming = detail?.upcoming_tasks || [];

  return (
    <Card title="Component Detail" subtitle={`${component.component_code} - ${component.component_type}`}>
      <div className="structure-component-detail">
        <div className="split-row">
          <div>
            <h3>{component.component_name}</h3>
            <p>{component.description}</p>
          </div>
          <StatusBadge status={component.condition} />
        </div>

        <div className={hasMonitoring ? "component-message ai-learning" : "no-sensor-panel"}>
          <strong>{hasMonitoring ? "Condition monitoring available." : "No direct sensor data available."}</strong>
          <p>
            {hasMonitoring
              ? "This component can use sensor or CBM history together with work orders and technician feedback."
              : "This component is managed using maintenance history, inspection tasks, replacement interval, and technician feedback."}
          </p>
        </div>

        <dl className="component-detail-grid">
          <div className="component-fact"><span>Criticality</span><strong>{component.criticality}</strong></div>
          <div className="component-fact"><span>Health</span><strong>{component.health_score === null || component.health_score === undefined ? "Not available" : `${formatNumber(component.health_score, 0)}%`}</strong></div>
          <div className="component-fact"><span>Last maintenance</span><strong>{formatDate(component.last_maintenance_date)}</strong></div>
          <div className="component-fact"><span>Next planned</span><strong>{formatDate(component.next_planned_maintenance)}</strong></div>
        </dl>

        <div>
          <h4>Maintenance Strategy</h4>
          <p>{component.maintenance_strategy}</p>
        </div>

        <div>
          <h4>Frequent Failures</h4>
          <div className="failure-chip-list">
            {component.frequent_failures.length ? component.frequent_failures.map((failure) => (
              <span className="badge badge-warning" key={failure}>{failure}</span>
            )) : <span className="muted">No repeated component failures captured.</span>}
          </div>
        </div>

        <div>
          <h4>AI Recommendation</h4>
          <p>{detail?.ai_recommendation || component.recommended_action || "I am still learning from the available maintenance data. More maintenance history and technician feedback will improve this recommendation."}</p>
        </div>

        <PreviewList
          title="Maintenance History Preview"
          empty="No past maintenance history available for this component yet."
          items={history.map((item) => `${formatDate(item.date)} - ${item.action_taken}`)}
        />
        <PreviewList
          title="Upcoming Task Preview"
          empty="No upcoming maintenance tasks available for this component yet."
          items={upcoming.map((task) => `${formatDate(task.planned_date)} - ${task.task_name} (${task.status})`)}
        />
      </div>
    </Card>
  );
}

function PreviewList({ title, empty, items }: { title: string; empty: string; items: string[] }) {
  return (
    <div>
      <h4>{title}</h4>
      {items.length ? (
        <ul className="structure-preview-list">
          {items.slice(0, 4).map((item) => <li key={item}>{item}</li>)}
        </ul>
      ) : (
        <p className="muted">{empty}</p>
      )}
    </div>
  );
}

function StructureFact({ icon: Icon, label, value }: { icon: typeof Boxes; label: string; value: string }) {
  return (
    <div className="structure-fact-card">
      <Icon size={18} />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function buildStats(components: AssetComponent[]) {
  const withSensors = components.filter((component) => component.has_sensor_data || component.has_cbm).length;
  const nextMaintenance = components
    .map((component) => component.next_planned_maintenance)
    .filter((date): date is string => Boolean(date))
    .sort()[0] || null;
  return {
    total: components.length,
    withSensors,
    withoutSensors: components.length - withSensors,
    nextMaintenance,
  };
}

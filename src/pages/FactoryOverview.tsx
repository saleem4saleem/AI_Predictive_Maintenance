import { Download, Plus, RefreshCw } from "lucide-react";
import { CriticalAssetsCard } from "../components/overview/CriticalAssetsCard";
import { DowntimeRiskCard } from "../components/overview/DowntimeRiskCard";
import { FactoryHealthCard } from "../components/overview/FactoryHealthCard";
import { OpenActionsCard } from "../components/overview/OpenActionsCard";
import { ProcessFlowOverview } from "../components/overview/ProcessFlowOverview";
import { ProductionFlow } from "../components/overview/ProductionFlow";
import { Card } from "../components/common/Card";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingSkeleton } from "../components/common/LoadingSkeleton";
import { PageHeader } from "../components/layout/PageHeader";
import { useFactoryOverview } from "../hooks/useFactoryOverview";
import { filterVisibleProductionAssets, getProductionAssetDisplayName } from "../utils/assetImageMap";
import type { PageKey } from "../App";

interface FactoryOverviewProps {
  selectedAssetId: number;
  onSelectAsset: (assetId: number) => void;
  onNavigate: (page: PageKey) => void;
}

export function FactoryOverview({ selectedAssetId, onSelectAsset, onNavigate }: FactoryOverviewProps) {
  const { data, loading, error, refresh } = useFactoryOverview();

  if (loading) return <LoadingSkeleton rows={8} />;
  if (error || !data) return <ErrorState message={error || "Backend is not reachable. Please check the API server."} onRetry={refresh} />;

  const productionFlowAssets = filterVisibleProductionAssets(data.production_flow);
  const overviewAssets = filterVisibleProductionAssets(data.assets);
  const visibleCriticalAssets = overviewAssets.filter((asset) => ["high", "critical"].includes(asset.risk_level)).length;
  const visibleOpenActions = overviewAssets.reduce((total, asset) => total + asset.open_actions, 0);

  function handleSelect(assetId: number) {
    onSelectAsset(assetId);
    onNavigate("asset-detail");
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow={data.factory_name}
        title="Factory Overview"
        description="A fast production-flow view of asset health, risk, maintenance timing, and AI-backed recommendations."
        actions={
          <>
            <button className="secondary-button" type="button" onClick={refresh}><RefreshCw size={16} /> Refresh</button>
            <button className="secondary-button" type="button"><Download size={16} /> Export</button>
            <button className="primary-button" type="button"><Plus size={16} /> Add Action</button>
          </>
        }
      />

      <div className="kpi-grid">
        <FactoryHealthCard value={data.factory_health} />
        <CriticalAssetsCard value={visibleCriticalAssets} />
        <OpenActionsCard value={visibleOpenActions} />
        <DowntimeRiskCard value={data.weekly_downtime_risk_hours} />
      </div>

      <ProductionFlow assets={productionFlowAssets} selectedAssetId={selectedAssetId} onSelectAsset={handleSelect} />

      <Card title="Asset Overview Table" subtitle="Same backend overview data, optimized for scanning.">
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Asset</th>
                <th>Status</th>
                <th>Risk</th>
                <th>Health</th>
                <th>Open Actions</th>
              </tr>
            </thead>
            <tbody>
              {overviewAssets.map((asset) => (
                <tr key={asset.asset_id} onClick={() => handleSelect(asset.asset_id)}>
                  <td><strong>{getProductionAssetDisplayName(asset)}</strong><span>{asset.asset_code}</span></td>
                  <td>{asset.status}</td>
                  <td>{asset.risk_level}</td>
                  <td>{asset.health_score.toFixed(0)}%</td>
                  <td>{asset.open_actions}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <ProcessFlowOverview assets={productionFlowAssets} selectedAssetId={selectedAssetId} onSelectAsset={handleSelect} />
    </div>
  );
}

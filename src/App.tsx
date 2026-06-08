import { AppLayout } from "./components/layout/AppLayout";
import { ErrorState } from "./components/common/ErrorState";
import { LoadingSkeleton } from "./components/common/LoadingSkeleton";
import { AssetDetail } from "./pages/AssetDetail";
import { AssetStructure } from "./pages/AssetStructure";
import { FactoryOverview } from "./pages/FactoryOverview";
import { KnowledgeSearch } from "./pages/KnowledgeSearch";
import { AIAssistant } from "./pages/AIAssistant";
import { KPIDashboard } from "./pages/KPIDashboard";
import { MaintenancePlanner } from "./pages/MaintenancePlanner";
import { MaintenanceNotifications } from "./pages/MaintenanceNotifications";
import { PredictiveMaintenance } from "./pages/PredictiveMaintenance";
import { SensorMonitoring } from "./pages/SensorMonitoring";
import { useAssets } from "./hooks/useAssets";
import { filterVisibleProductionAssets } from "./utils/assetImageMap";
import { useState } from "react";
import type { MaintenanceNotificationDraft } from "./types/maintenanceNotification";

export type PageKey =
  | "overview"
  | "asset-structure"
  | "asset-detail"
  | "sensor-monitoring"
  | "predictive-maintenance"
  | "maintenance-planner"
  | "maintenance-notifications"
  | "ai-assistant"
  | "knowledge-search"
  | "kpi-dashboard";

function App() {
  const assets = useAssets();
  const [activePage, setActivePage] = useState<PageKey>("overview");
  const [selectedAssetId, setSelectedAssetId] = useState(6);
  const [notificationDraft, setNotificationDraft] = useState<MaintenanceNotificationDraft | null>(null);

  const assetList = filterVisibleProductionAssets(assets.data || []);
  const selectedAssetExists = assetList.some((asset) => asset.asset_id === selectedAssetId);
  const safeSelectedAssetId = selectedAssetExists ? selectedAssetId : assetList[0]?.asset_id || 1;

  function handleSelectAsset(assetId: number) {
    setSelectedAssetId(assetId);
  }

  function openMaintenanceNotification(draft: MaintenanceNotificationDraft) {
    if (draft.asset_id) {
      setSelectedAssetId(draft.asset_id);
    }
    setNotificationDraft(draft);
    setActivePage("maintenance-notifications");
  }

  function renderPage() {
    switch (activePage) {
      case "overview":
        return <FactoryOverview selectedAssetId={safeSelectedAssetId} onSelectAsset={handleSelectAsset} onNavigate={setActivePage} />;
      case "asset-structure":
        return (
          <AssetStructure
            assetId={safeSelectedAssetId}
            assets={assetList}
            onSelectAsset={handleSelectAsset}
            onOpenAssetDetail={() => setActivePage("asset-detail")}
          />
        );
      case "asset-detail":
        return <AssetDetail assetId={safeSelectedAssetId} onCreateNotification={openMaintenanceNotification} />;
      case "sensor-monitoring":
        return (
          <SensorMonitoring
            assetId={safeSelectedAssetId}
            assets={assetList}
            onSelectAsset={handleSelectAsset}
            onCreateNotification={openMaintenanceNotification}
          />
        );
      case "predictive-maintenance":
        return <PredictiveMaintenance assetId={safeSelectedAssetId} onCreateNotification={openMaintenanceNotification} />;
      case "maintenance-planner":
        return <MaintenancePlanner assetId={safeSelectedAssetId} />;
      case "maintenance-notifications":
        return (
          <MaintenanceNotifications
            assetId={safeSelectedAssetId}
            assets={assetList}
            onSelectAsset={handleSelectAsset}
            initialDraft={notificationDraft}
            onDraftConsumed={() => setNotificationDraft(null)}
          />
        );
      case "ai-assistant":
        return <AIAssistant assetId={safeSelectedAssetId} assets={assetList} onSelectAsset={handleSelectAsset} />;
      case "knowledge-search":
        return <KnowledgeSearch assetId={safeSelectedAssetId} />;
      case "kpi-dashboard":
        return <KPIDashboard assetId={safeSelectedAssetId} assets={assetList} onSelectAsset={handleSelectAsset} />;
      default:
        return <FactoryOverview selectedAssetId={safeSelectedAssetId} onSelectAsset={handleSelectAsset} onNavigate={setActivePage} />;
    }
  }

  if (assets.loading) {
    return (
      <div className="boot-screen">
        <LoadingSkeleton rows={6} />
      </div>
    );
  }

  if (assets.error || assetList.length === 0) {
    return (
      <div className="boot-screen">
        <ErrorState message={assets.error || "Backend is not reachable. Please check the API server."} onRetry={assets.refresh} />
      </div>
    );
  }

  return (
    <AppLayout
      activePage={activePage}
      assets={assetList}
      selectedAssetId={safeSelectedAssetId}
      onNavigate={setActivePage}
      onSelectAsset={handleSelectAsset}
      onRefresh={assets.refresh}
    >
      {renderPage()}
    </AppLayout>
  );
}

export default App;

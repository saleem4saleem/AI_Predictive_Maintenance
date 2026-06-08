import { Bell, RefreshCw, Search, UserCircle } from "lucide-react";
import type { AssetBasicResponse } from "../../types/asset";
import { getProductionAssetDisplayName } from "../../utils/assetImageMap";

interface TopbarProps {
  assets: AssetBasicResponse[];
  selectedAssetId: number;
  onSelectAsset: (assetId: number) => void;
  onRefresh: () => void;
}

export function Topbar({ assets, selectedAssetId, onSelectAsset, onRefresh }: TopbarProps) {
  return (
    <header className="topbar">
      <div>
        <h1>Smart Predictive Maintenance System</h1>
        <p>Glass factory asset health, prediction, and maintenance planning</p>
      </div>

      <div className="topbar-controls">
        <label className="asset-select">
          <span>Selected Asset</span>
          <select value={selectedAssetId} onChange={(event) => onSelectAsset(Number(event.target.value))}>
            {assets.map((asset) => (
              <option key={asset.asset_id} value={asset.asset_id}>
                {getProductionAssetDisplayName(asset)}
              </option>
            ))}
          </select>
        </label>

        <div className="search-box">
          <Search size={16} />
          <input aria-label="Search" placeholder="Search assets, sensors, alerts..." />
        </div>

        <button className="icon-button" type="button" onClick={onRefresh} title="Refresh data">
          <RefreshCw size={18} />
        </button>
        <button className="icon-button" type="button" title="Notifications">
          <Bell size={18} />
        </button>
        <div className="user-badge">
          <UserCircle size={22} />
          <span>MS</span>
        </div>
      </div>
    </header>
  );
}

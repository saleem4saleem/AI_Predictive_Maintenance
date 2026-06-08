import type { ProductionFlowAsset } from "../../types/overview";
import {
  getAssetIllustrationFallback,
  getAssetIllustrationUrl,
  getProductionAssetDisplayName,
} from "../../utils/assetImageMap";
import { formatDate } from "../../utils/date";
import { StatusBadge } from "../common/StatusBadge";
import { RiskBadge } from "../common/RiskBadge";

interface AssetFlowCardProps {
  asset: ProductionFlowAsset;
  orderNumber: number;
  selected: boolean;
  onSelect: (assetId: number) => void;
}

export function AssetFlowCard({ asset, orderNumber, selected, onSelect }: AssetFlowCardProps) {
  const machineIconUrl = getAssetIllustrationUrl(asset.asset_code);
  const displayName = getProductionAssetDisplayName(asset);

  return (
    <button className={selected ? "flow-card selected" : "flow-card"} type="button" onClick={() => onSelect(asset.asset_id)}>
      <span className="flow-card-number">{orderNumber}</span>
      <div className="flow-icon">
        {machineIconUrl ? (
          <img className="machine-icon-image" src={machineIconUrl} alt={`${displayName} illustration`} loading="lazy" />
        ) : (
          <span className="machine-icon-fallback" role="img" aria-label={`${displayName} illustration placeholder`}>
            {getAssetIllustrationFallback(asset)}
          </span>
        )}
      </div>
      <h3>{displayName}</h3>
      <div className="flow-badges">
        <StatusBadge status={asset.status} />
        <RiskBadge risk={asset.risk_level} />
      </div>
      <div className="health-meter">
        <span style={{ width: `${asset.health_score}%` }} />
      </div>
      <dl className="mini-facts">
        <div>
          <dt>Health</dt>
          <dd>{asset.health_score.toFixed(0)}%</dd>
        </div>
        <div>
          <dt>Next PM</dt>
          <dd>{formatDate(asset.next_planned_maintenance)}</dd>
        </div>
      </dl>
      {asset.predicted_failure_date && (
        <p className="prediction-note">Predicted risk: {formatDate(asset.predicted_failure_date)}</p>
      )}
    </button>
  );
}

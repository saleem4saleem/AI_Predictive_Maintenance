import type { AssetBasicResponse } from "../../types/asset";
import { RiskBadge } from "../common/RiskBadge";
import { StatusBadge } from "../common/StatusBadge";

export function AssetHeader({ asset }: { asset: AssetBasicResponse }) {
  return (
    <div className="asset-header">
      <div>
        <span className="eyebrow">{asset.asset_code}</span>
        <h1>{asset.asset_name}</h1>
        <p>{asset.asset_type} · {asset.location || "Unknown location"} · Criticality {asset.criticality}</p>
      </div>
      <div className="asset-header-badges">
        <StatusBadge status={asset.status} />
        <RiskBadge risk={asset.risk_level} />
      </div>
    </div>
  );
}

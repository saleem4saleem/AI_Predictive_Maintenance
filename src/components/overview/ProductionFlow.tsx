import { ArrowRight } from "lucide-react";
import type { ProductionFlowAsset } from "../../types/overview";
import { filterVisibleProductionAssets } from "../../utils/assetImageMap";
import { Card } from "../common/Card";
import { AssetFlowCard } from "./AssetFlowCard";

interface ProductionFlowProps {
  assets: ProductionFlowAsset[];
  selectedAssetId: number;
  onSelectAsset: (assetId: number) => void;
}

export function ProductionFlow({ assets, selectedAssetId, onSelectAsset }: ProductionFlowProps) {
  const visibleAssets = filterVisibleProductionAssets(assets);

  return (
    <Card title="Production Flow Assets" subtitle="Click an asset to open its predictive maintenance detail view.">
      <div className="flow-grid">
        {visibleAssets.map((asset, index) => (
          <div className="flow-step" key={asset.asset_id}>
            <AssetFlowCard
              asset={asset}
              orderNumber={index + 1}
              selected={asset.asset_id === selectedAssetId}
              onSelect={onSelectAsset}
            />
            {index < visibleAssets.length - 1 && <ArrowRight className="flow-arrow" size={22} />}
          </div>
        ))}
      </div>
    </Card>
  );
}

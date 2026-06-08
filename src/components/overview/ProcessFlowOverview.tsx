import { ArrowRight } from "lucide-react";
import type { ProductionFlowAsset } from "../../types/overview";
import {
  getAssetIllustrationFallback,
  getAssetIllustrationUrl,
  getProductionAssetDisplayName,
} from "../../utils/assetImageMap";
import { Card } from "../common/Card";

interface ProcessFlowOverviewProps {
  assets: ProductionFlowAsset[];
  selectedAssetId: number;
  onSelectAsset: (assetId: number) => void;
}

export function ProcessFlowOverview({ assets, selectedAssetId, onSelectAsset }: ProcessFlowOverviewProps) {
  return (
    <Card title="Process Flow Overview" subtitle="Reduced production sequence ending at Packaging Machine.">
      <div className="process-flow-strip">
        {assets.map((asset, index) => {
          const imageUrl = getAssetIllustrationUrl(asset.asset_code);
          const displayName = getProductionAssetDisplayName(asset);

          return (
            <div className="process-flow-step" key={asset.asset_id}>
              <button
                className={selectedAssetId === asset.asset_id ? "process-node selected" : "process-node"}
                type="button"
                onClick={() => onSelectAsset(asset.asset_id)}
              >
                <span className="process-node-visual">
                  {imageUrl ? (
                    <img src={imageUrl} alt={`${displayName} illustration`} loading="lazy" />
                  ) : (
                    <span>{getAssetIllustrationFallback(asset)}</span>
                  )}
                </span>
                <span>{displayName}</span>
              </button>
              {index < assets.length - 1 && <ArrowRight className="process-arrow" size={18} />}
            </div>
          );
        })}
      </div>
    </Card>
  );
}

import type { ReactNode } from "react";
import type { PageKey } from "../../App";
import type { AssetBasicResponse } from "../../types/asset";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

interface AppLayoutProps {
  activePage: PageKey;
  assets: AssetBasicResponse[];
  selectedAssetId: number;
  onNavigate: (page: PageKey) => void;
  onSelectAsset: (assetId: number) => void;
  onRefresh: () => void;
  children: ReactNode;
}

export function AppLayout({
  activePage,
  assets,
  selectedAssetId,
  onNavigate,
  onSelectAsset,
  onRefresh,
  children,
}: AppLayoutProps) {
  return (
    <div className="app-shell">
      <Sidebar activePage={activePage} onNavigate={onNavigate} />
      <div className="workspace">
        <Topbar
          assets={assets}
          selectedAssetId={selectedAssetId}
          onSelectAsset={onSelectAsset}
          onRefresh={onRefresh}
        />
        <main className="main-content">{children}</main>
      </div>
    </div>
  );
}

import {
  Activity,
  BarChart3,
  BellRing,
  Bot,
  Building2,
  CalendarClock,
  ClipboardList,
  Database,
  Factory,
  Gauge,
  Search,
} from "lucide-react";
import { companyLogoUrl } from "../../assets/branding";
import type { PageKey } from "../../App";

const navItems: Array<{ key: PageKey; label: string; icon: typeof Factory }> = [
  { key: "overview", label: "Factory Overview", icon: Factory },
  { key: "asset-structure", label: "Asset Structure", icon: Building2 },
  { key: "asset-detail", label: "Asset Detail", icon: ClipboardList },
  { key: "sensor-monitoring", label: "Condition Monitoring", icon: Activity },
  { key: "predictive-maintenance", label: "Predictive Maintenance", icon: Gauge },
  { key: "maintenance-planner", label: "Maintenance Planner", icon: CalendarClock },
  { key: "maintenance-notifications", label: "Maintenance Notifications", icon: BellRing },
  { key: "ai-assistant", label: "AI Assistant", icon: Bot },
  { key: "knowledge-search", label: "Knowledge Search", icon: Search },
  { key: "kpi-dashboard", label: "KPI Dashboard", icon: BarChart3 },
];

interface SidebarProps {
  activePage: PageKey;
  onNavigate: (page: PageKey) => void;
}

export function Sidebar({ activePage, onNavigate }: SidebarProps) {
  return (
    <aside className="app-sidebar">
      <div className="brand-block">
        <div className="brand-mark">
          {companyLogoUrl ? (
            <img className="company-logo" src={companyLogoUrl} alt="Company logo" />
          ) : (
            "A"
          )}
        </div>
        <div>
          <strong>Ardagh</strong>
          <span>Smart Maintenance</span>
        </div>
      </div>

      <nav className="sidebar-nav" aria-label="Main navigation">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              className={activePage === item.key ? "nav-item active" : "nav-item"}
              key={item.key}
              type="button"
              onClick={() => onNavigate(item.key)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <Database size={16} />
        <span>API-first backend</span>
      </div>
    </aside>
  );
}

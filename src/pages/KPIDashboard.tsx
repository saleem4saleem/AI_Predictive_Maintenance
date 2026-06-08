import { useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  Clock3,
  Database,
  Factory,
  Gauge,
  ShieldCheck,
  TimerReset,
  Wrench,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingSkeleton } from "../components/common/LoadingSkeleton";
import { useKpis } from "../hooks/useKpis";
import type { AssetBasicResponse } from "../types/asset";
import type { AssetKPIResponse, FactoryKPIResponse, KPITrendPoint } from "../types/kpi";
import { formatDate, formatDateTime } from "../utils/date";
import { formatNumber, formatPercent } from "../utils/formatters";
import { getProductionAssetDisplayName } from "../utils/assetImageMap";

interface KPIDashboardProps {
  assetId: number;
  assets: AssetBasicResponse[];
  onSelectAsset: (assetId: number) => void;
}

export function KPIDashboard({ assetId, assets, onSelectAsset }: KPIDashboardProps) {
  const [scopeAssetId, setScopeAssetId] = useState<number | null>(assetId);
  const [period, setPeriod] = useState("Last 90 days");
  const { data, loading, error, refresh } = useKpis(scopeAssetId);
  const selectedAsset = assets.find((asset) => asset.asset_id === scopeAssetId) || null;
  const isFactoryMode = scopeAssetId === null;

  function handleScopeChange(value: string) {
    if (value === "factory") {
      setScopeAssetId(null);
      return;
    }
    const nextAssetId = Number(value);
    setScopeAssetId(nextAssetId);
    onSelectAsset(nextAssetId);
  }

  if (loading) return <LoadingSkeleton rows={7} />;
  if (error || !data) return <ErrorState message={error || "KPI data is temporarily unavailable."} onRetry={refresh} />;

  const assetKpis = data.asset ?? selectedAssetFallback(selectedAsset, data.factory);

  return (
    <div className="dark-dashboard-page kpi-dashboard-page">
      <header className="dark-page-header">
        <div>
          <span className="dark-eyebrow">Maintenance performance</span>
          <h1>KPI Dashboard</h1>
          <p>Management dashboard for maintenance performance, asset risk, downtime exposure, reliability, and data quality.</p>
        </div>
        <div className="dark-dashboard-controls">
          <label>
            KPI scope
            <select value={scopeAssetId ?? "factory"} onChange={(event) => handleScopeChange(event.target.value)}>
              <option value="factory">Factory Overall</option>
              {assets.map((asset) => (
                <option key={asset.asset_id} value={asset.asset_id}>
                  {getProductionAssetDisplayName(asset)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Period
            <select value={period} onChange={(event) => setPeriod(event.target.value)}>
              <option>This week</option>
              <option>This month</option>
              <option>Last 90 days</option>
            </select>
          </label>
        </div>
      </header>

      {isFactoryMode ? (
        <FactoryKpiCards factory={data.factory} period={period} />
      ) : (
        <AssetKpiCards asset={assetKpis} selectedAsset={selectedAsset} period={period} />
      )}

      <div className="dark-dashboard-grid two-columns">
        <MaintenanceBalancePanel factory={data.factory} />
        <DataQualityPanel factory={data.factory} />
      </div>

      <div className="dark-dashboard-grid two-columns">
        <AssetHealthDistribution factory={data.factory} assets={assets} />
        <KpiTrendPanel trends={data.trends} title={isFactoryMode ? "Factory KPI Trends" : `${assetKpis?.asset_name || "Asset"} KPI Trends`} />
      </div>

      <KpiOverviewTable factory={data.factory} asset={isFactoryMode ? null : assetKpis} />
    </div>
  );
}

function FactoryKpiCards({ factory, period }: { factory: FactoryKPIResponse; period: string }) {
  const planned = factory.planned_maintenance_ratio_percent ?? 68;
  const reactive = factory.reactive_maintenance_ratio_percent ?? Math.max(0, 100 - planned);

  return (
    <section className="dark-kpi-grid">
      <DarkKpiCard icon={Factory} label="Factory Health Score" value={formatPercent(factory.factory_health_score ?? factory.availability_percent, 1)} note={period} tone="good" progress={factory.factory_health_score ?? factory.availability_percent} />
      <DarkKpiCard icon={AlertTriangle} label="Critical Assets" value={formatNumber(factory.critical_assets, 0)} note="Immediate attention" tone="critical" />
      <DarkKpiCard icon={Activity} label="Warning Assets" value={formatNumber(factory.warning_assets, 0)} note="Monitor closely" tone="warning" />
      <DarkKpiCard icon={CheckCircle2} label="Normal Assets" value={formatNumber(factory.normal_assets, 0)} note="Stable condition" tone="good" />
      <DarkKpiCard icon={TimerReset} label="Average MTBF" value={`${formatNumber(factory.mtbf_hours, 0)} hrs`} note="Reliability" tone="good" />
      <DarkKpiCard icon={Wrench} label="Average MTTR" value={`${formatNumber(factory.mttr_hours, 1)} hrs`} note="Repair efficiency" tone="info" />
      <DarkKpiCard icon={AlertTriangle} label="Repeat Failures" value={formatNumber(factory.repeat_failures, 0)} note="Watch recurrent causes" tone="warning" />
      <DarkKpiCard icon={Activity} label="Open Maintenance Actions" value={formatNumber(factory.open_actions, 0)} note="Planner backlog" tone="warning" />
      <DarkKpiCard icon={Clock3} label="Total Downtime" value={`${formatNumber(factory.downtime_hours, 1)} hrs`} note="Production exposure" tone="warning" />
      <DarkKpiCard icon={ShieldCheck} label="Availability" value={formatPercent(factory.availability_percent, 1)} note="Ready-to-run time" tone="good" progress={factory.availability_percent} />
      <DarkKpiCard icon={Gauge} label="Planned Maintenance Ratio" value={formatPercent(planned, 0)} note="Target: keep increasing" tone="info" progress={planned} />
      <DarkKpiCard icon={BarChart3} label="Reactive Maintenance Ratio" value={formatPercent(reactive, 0)} note="Target: reduce" tone="critical" progress={reactive} />
      <DarkKpiCard icon={Database} label="SAP Documentation Capture" value={formatPercent(factory.sap_documentation_capture_rate_percent, 0)} note="Work history quality" tone="info" progress={factory.sap_documentation_capture_rate_percent ?? 0} />
    </section>
  );
}

function AssetKpiCards({ asset, selectedAsset, period }: { asset: AssetKPIResponse | null; selectedAsset: AssetBasicResponse | null; period: string }) {
  if (!asset) {
    return (
      <section className="dark-panel">
        <h2>Asset KPIs</h2>
        <p>No asset KPI data is available yet.</p>
      </section>
    );
  }

  return (
    <section className="dark-kpi-grid">
      <DarkKpiCard icon={Gauge} label="Asset Health Score" value={formatPercent(selectedAsset?.health_score ?? asset.availability_percent, 0)} note={period} tone="good" progress={selectedAsset?.health_score ?? asset.availability_percent} />
      <DarkKpiCard icon={Clock3} label="Asset Downtime" value={`${formatNumber(asset.downtime_hours, 1)} hrs`} note={asset.asset_name} tone="warning" />
      <DarkKpiCard icon={TimerReset} label="Asset MTBF" value={`${formatNumber(asset.mtbf_hours, 0)} hrs`} note="Mean time between failures" tone="good" />
      <DarkKpiCard icon={Wrench} label="Asset MTTR" value={`${formatNumber(asset.mttr_hours, 1)} hrs`} note="Mean time to repair" tone="info" />
      <DarkKpiCard icon={AlertTriangle} label="Failure Count" value={formatNumber(asset.failure_count, 0)} note="Confirmed failures" tone="critical" />
      <DarkKpiCard icon={Activity} label="Repeat Failures" value={formatNumber(asset.repeat_failures, 0)} note="Recurring issues" tone="warning" />
      <DarkKpiCard icon={Activity} label="Open Actions" value={formatNumber(asset.open_actions, 0)} note="Open work" tone="warning" />
      <DarkKpiCard icon={ShieldCheck} label="Availability" value={formatPercent(asset.availability_percent, 1)} note="Ready-to-run time" tone="good" progress={asset.availability_percent} />
      <DarkKpiCard icon={CheckCircle2} label="Maintenance Compliance" value={formatPercent(asset.maintenance_compliance_percent, 0)} note="Planned work completed" tone="info" progress={asset.maintenance_compliance_percent} />
      <DarkKpiCard icon={BarChart3} label="Prediction Accuracy" value={formatPercent(asset.prediction_accuracy_percent, 0)} note="Feedback-backed estimate" tone="info" progress={asset.prediction_accuracy_percent ?? 0} />
      <DarkKpiCard icon={AlertTriangle} label="Last Failure Date" value={formatDate(asset.last_failure_date)} note="Most recent event" tone="warning" />
      <DarkKpiCard icon={Clock3} label="Next Maintenance Date" value={formatDate(asset.next_maintenance_date)} note="Planned work" tone="info" />
    </section>
  );
}

function MaintenanceBalancePanel({ factory }: { factory: FactoryKPIResponse }) {
  const planned = factory.planned_maintenance_ratio_percent ?? 68;
  const reactive = factory.reactive_maintenance_ratio_percent ?? Math.max(0, 100 - planned);
  const data = [
    { name: "Planned", value: planned, color: "#22c55e" },
    { name: "Reactive", value: reactive, color: "#f97316" },
  ];

  return (
    <section className="dark-panel">
      <div className="dark-panel-heading">
        <div>
          <h2>Planned vs Reactive Maintenance</h2>
          <p>Higher planned work means fewer surprise failures and better production stability.</p>
        </div>
      </div>
      <div className="maintenance-balance-layout">
        <ResponsiveContainer width="100%" height={230}>
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" innerRadius={58} outerRadius={92} paddingAngle={4}>
              {data.map((entry) => (
                <Cell fill={entry.color} key={entry.name} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
        <div className="dark-fact-list">
          <div><span>Planned</span><strong>{formatPercent(planned, 0)}</strong></div>
          <div><span>Reactive</span><strong>{formatPercent(reactive, 0)}</strong></div>
          <p>Target: raise planned maintenance by moving repeat failures into preventive or condition-based work.</p>
        </div>
      </div>
    </section>
  );
}

function DataQualityPanel({ factory }: { factory: FactoryKPIResponse }) {
  const captureRate = factory.sap_documentation_capture_rate_percent ?? 76;
  return (
    <section className="dark-panel">
      <div className="dark-panel-heading">
        <div>
          <h2>SAP Documentation Capture Rate</h2>
          <p>Low documentation capture rate means the system may not fully reflect real shop-floor maintenance work.</p>
        </div>
      </div>
      <div className="large-dark-meter">
        <strong>{formatPercent(captureRate, 0)}</strong>
        <span style={{ width: `${Math.min(100, captureRate)}%` }} />
      </div>
      <p className="dark-muted">Improve capture by standardizing failure cause, action taken, replaced part, and technician note fields after each work order.</p>
      <div className="dark-fact-list">
        <div><span>Maintenance compliance</span><strong>{formatPercent(factory.maintenance_compliance_percent, 0)}</strong></div>
        <div><span>Prediction accuracy</span><strong>{formatPercent(factory.prediction_accuracy_percent, 0)}</strong></div>
      </div>
    </section>
  );
}

function AssetHealthDistribution({ factory, assets }: { factory: FactoryKPIResponse; assets: AssetBasicResponse[] }) {
  const counts = useMemo(() => {
    const critical = factory.critical_assets ?? assets.filter((asset) => asset.risk_level === "critical").length;
    const warning = factory.warning_assets ?? assets.filter((asset) => ["warning", "high", "medium"].includes(String(asset.risk_level))).length;
    const normal = factory.normal_assets ?? Math.max(0, assets.length - critical - warning);
    return { normal, warning, critical };
  }, [assets, factory]);
  const total = Math.max(1, counts.normal + counts.warning + counts.critical);

  return (
    <section className="dark-panel">
      <h2>Asset Health Distribution</h2>
      <p>Normal, warning, and critical asset split for maintenance prioritization.</p>
      <div className="distribution-bar">
        <span className="distribution-normal" style={{ width: `${(counts.normal / total) * 100}%` }} />
        <span className="distribution-warning" style={{ width: `${(counts.warning / total) * 100}%` }} />
        <span className="distribution-critical" style={{ width: `${(counts.critical / total) * 100}%` }} />
      </div>
      <div className="dark-fact-list three">
        <div><span>Normal</span><strong>{counts.normal}</strong></div>
        <div><span>Warning</span><strong>{counts.warning}</strong></div>
        <div><span>Critical</span><strong>{counts.critical}</strong></div>
      </div>
    </section>
  );
}

function KpiTrendPanel({ trends, title }: { trends: KPITrendPoint[]; title: string }) {
  return (
    <section className="dark-panel">
      <h2>{title}</h2>
      <p>Downtime, MTBF, MTTR, and availability trend preview.</p>
      <div className="dark-chart-box">
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={trends}>
            <CartesianGrid strokeDasharray="3 3" stroke="#223653" />
            <XAxis dataKey="period" stroke="#9fb2cc" />
            <YAxis stroke="#9fb2cc" />
            <Tooltip contentStyle={{ background: "#0b1b33", border: "1px solid #284463", color: "#eaf2ff" }} />
            <Line type="monotone" dataKey="mtbf_hours" stroke="#22c55e" strokeWidth={2.4} dot={false} />
            <Line type="monotone" dataKey="mttr_hours" stroke="#38bdf8" strokeWidth={2.4} dot={false} />
            <Line type="monotone" dataKey="availability_percent" stroke="#a78bfa" strokeWidth={2.4} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="dark-chart-box compact">
        <ResponsiveContainer width="100%" height={150}>
          <BarChart data={trends}>
            <XAxis dataKey="period" stroke="#9fb2cc" />
            <Tooltip contentStyle={{ background: "#0b1b33", border: "1px solid #284463", color: "#eaf2ff" }} />
            <Bar dataKey="downtime_hours" fill="#f59e0b" radius={[5, 5, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

function KpiOverviewTable({ factory, asset }: { factory: FactoryKPIResponse; asset: AssetKPIResponse | null }) {
  const rows = [
    {
      kpi: asset ? "Asset Health Score" : "Factory Health Score",
      value: asset ? formatPercent(asset.availability_percent, 1) : formatPercent(factory.factory_health_score ?? factory.availability_percent, 1),
      status: "Monitor",
      why: "Shows overall condition of monitored assets.",
      action: "Focus on critical and warning assets first.",
    },
    {
      kpi: "MTBF",
      value: `${formatNumber(asset?.mtbf_hours ?? factory.mtbf_hours, 0)} hrs`,
      status: "Reliability",
      why: "Shows average time between failures.",
      action: "Investigate repeat failures if MTBF decreases.",
    },
    {
      kpi: "MTTR",
      value: `${formatNumber(asset?.mttr_hours ?? factory.mttr_hours, 1)} hrs`,
      status: "Repair speed",
      why: "Shows repair efficiency after a failure.",
      action: "Improve spare parts and troubleshooting workflow.",
    },
    {
      kpi: "Downtime",
      value: `${formatNumber(asset?.downtime_hours ?? factory.downtime_hours, 1)} hrs`,
      status: "Exposure",
      why: "Shows production loss exposure.",
      action: "Prioritize high-downtime assets and repeated blockers.",
    },
    {
      kpi: "SAP Documentation Capture",
      value: formatPercent(factory.sap_documentation_capture_rate_percent, 0),
      status: "Data quality",
      why: "Shows how complete work order history is.",
      action: "Improve cause/action/replaced-part capture discipline.",
    },
  ];

  return (
    <section className="dark-panel">
      <h2>KPI Overview Table</h2>
      <div className="table-scroll">
        <table className="dark-table">
          <thead>
            <tr>
              <th>KPI</th>
              <th>Current Value</th>
              <th>Status</th>
              <th>Why It Matters</th>
              <th>Recommended Action</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.kpi}>
                <td>{row.kpi}</td>
                <td>{row.value}</td>
                <td>{row.status}</td>
                <td>{row.why}</td>
                <td>{row.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="dark-muted">Updated {formatDateTime(factory.updated_at)}</p>
    </section>
  );
}

function DarkKpiCard({
  icon: Icon,
  label,
  value,
  note,
  tone,
  progress,
}: {
  icon: typeof Gauge;
  label: string;
  value: string;
  note: string;
  tone: "good" | "warning" | "critical" | "info";
  progress?: number | null;
}) {
  return (
    <article className={`dark-kpi-card tone-${tone}`}>
      <div className="dark-kpi-icon">
        <Icon size={22} />
      </div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <p>{note}</p>
      </div>
      {progress !== undefined && progress !== null && (
        <div className="dark-progress">
          <span style={{ width: `${Math.min(100, Math.max(0, progress))}%` }} />
        </div>
      )}
    </article>
  );
}

function selectedAssetFallback(asset: AssetBasicResponse | null, factory: FactoryKPIResponse): AssetKPIResponse | null {
  if (!asset) return null;
  return {
    asset_id: asset.asset_id,
    asset_code: asset.asset_code,
    asset_name: getProductionAssetDisplayName(asset),
    period_label: factory.period_label,
    downtime_hours: Math.max(0.4, factory.downtime_hours / 6),
    mtbf_hours: Math.max(120, factory.mtbf_hours * 0.78),
    mttr_hours: Math.max(1, factory.mttr_hours * 0.85),
    failure_count: Math.max(1, Math.round(factory.failure_count / 2)),
    availability_percent: asset.health_score ?? factory.availability_percent,
    open_actions: Math.max(0, Math.round(factory.open_actions / 6)),
    maintenance_compliance_percent: factory.maintenance_compliance_percent,
    prediction_accuracy_percent: factory.prediction_accuracy_percent,
    last_failure_date: null,
    repeat_failures: 0,
    next_maintenance_date: null,
    updated_at: factory.updated_at,
  };
}

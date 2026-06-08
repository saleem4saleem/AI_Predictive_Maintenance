import { Activity, AlertTriangle, BellRing, Clock3, Factory, Gauge, RadioTower, Thermometer, Zap } from "lucide-react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingSkeleton } from "../components/common/LoadingSkeleton";
import { useSensorData } from "../hooks/useSensorData";
import type { AssetBasicResponse } from "../types/asset";
import type { SensorLatestResponse } from "../types/sensor";
import type { MaintenanceNotificationDraft } from "../types/maintenanceNotification";
import { formatDateTime } from "../utils/date";
import { formatNumber } from "../utils/formatters";
import { getProductionAssetDisplayName } from "../utils/assetImageMap";

interface SensorMonitoringProps {
  assetId: number;
  assets: AssetBasicResponse[];
  onSelectAsset: (assetId: number) => void;
  onCreateNotification?: (draft: MaintenanceNotificationDraft) => void;
}

type SensorStatus = "normal" | "warning" | "critical";

interface SensorCardModel {
  key: keyof SensorLatestResponse;
  label: string;
  value: number;
  unit: string;
  status: SensorStatus;
  icon: typeof Activity;
  explanation: string;
}

export function SensorMonitoring({ assetId, assets, onSelectAsset, onCreateNotification }: SensorMonitoringProps) {
  const { data, loading, error, refresh } = useSensorData(assetId, 24);
  const selectedAsset = assets.find((asset) => asset.asset_id === assetId);
  const sensorCards = data ? buildSensorCards(data.latest) : [];
  const strongestSignal = sensorCards.slice().sort((left, right) => sensorWeight(right.status) - sensorWeight(left.status))[0];

  if (loading) return <LoadingSkeleton rows={6} />;
  if (error || !data) return <ErrorState message={error || "No recent sensor data available for this asset."} onRetry={refresh} />;

  return (
    <div className="dark-dashboard-page condition-page">
      <header className="dark-page-header">
        <div>
          <span className="dark-eyebrow">Condition monitoring</span>
          <h1>Condition Monitoring</h1>
          <p>Live condition monitoring view for the selected asset. Current demo mode uses simulated/sample sensor data and is ready for live sensor integration later.</p>
        </div>
        <div className="dark-dashboard-controls">
          <label>
            Selected Asset
            <select value={assetId} onChange={(event) => onSelectAsset(Number(event.target.value))}>
              {assets.map((asset) => (
                <option key={asset.asset_id} value={asset.asset_id}>
                  {getProductionAssetDisplayName(asset)}
                </option>
              ))}
            </select>
          </label>
        </div>
      </header>

      <section className="condition-top-grid">
        <DarkInfoCard icon={Factory} label="Selected Asset" value={selectedAsset ? getProductionAssetDisplayName(selectedAsset) : `Asset ${assetId}`} note={selectedAsset?.asset_type || "Production asset"} />
        <DarkInfoCard icon={Activity} label="Machine Status" value={selectedAsset?.status || "Unknown"} note={`Risk: ${selectedAsset?.risk_level || "unknown"}`} tone={statusTone(selectedAsset?.risk_level || selectedAsset?.status)} />
        <DarkInfoCard icon={Clock3} label="Last Updated" value={formatDateTime(data.latest.timestamp)} note="Latest backend sensor reading" />
      </section>

      {sensorCards.length > 0 ? (
        <section className="condition-sensor-grid">
          {sensorCards.map((sensor) => (
            <SensorCard sensor={sensor} key={String(sensor.key)} />
          ))}
        </section>
      ) : (
        <EmptyState title="No recent sensor data available for this asset." message="Sensor cards will appear when the backend returns asset-level condition data." />
      )}

      <div className="dark-dashboard-grid two-columns">
        <SensorTrendPreview history={data.history.history} />
        <SensorAiInsight
          asset={selectedAsset}
          assetName={selectedAsset ? getProductionAssetDisplayName(selectedAsset) : "Selected asset"}
          strongestSignal={strongestSignal}
          status={selectedAsset?.status || "unknown"}
          onCreateNotification={onCreateNotification}
        />
      </div>

      <SensorMeaningTable />
    </div>
  );
}

function buildSensorCards(latest: SensorLatestResponse): SensorCardModel[] {
  const definitions: Array<Omit<SensorCardModel, "value" | "status"> & { value: number | null | undefined }> = [
    {
      key: "vibration",
      label: "Vibration",
      value: latest.vibration,
      unit: "mm/s",
      icon: Activity,
      explanation: "Detects bearing wear, imbalance, misalignment, looseness, and gearbox problems.",
    },
    {
      key: "temperature",
      label: "Temperature",
      value: latest.temperature,
      unit: "C",
      icon: Thermometer,
      explanation: "Detects overheating, friction, poor lubrication, cooling problems, and overload.",
    },
    {
      key: "current_value",
      label: "Current Draw",
      value: latest.current_value,
      unit: "A",
      icon: Zap,
      explanation: "Detects motor overload, mechanical resistance, jams, electrical imbalance, and abnormal load.",
    },
    {
      key: "pressure",
      label: "Pressure",
      value: latest.pressure,
      unit: "bar",
      icon: Gauge,
      explanation: "Detects blockage, leakage, valve issues, pneumatic restriction, or unstable compressed air.",
    },
    {
      key: "speed",
      label: "Speed",
      value: latest.speed,
      unit: "rpm",
      icon: RadioTower,
      explanation: "Detects drive issue, belt slip, overload, mechanical resistance, and process instability.",
    },
    {
      key: "flow",
      label: "Flow",
      value: latest.flow,
      unit: "l/min",
      icon: Gauge,
      explanation: "Detects blockage, leakage, pump degradation, valve restriction, or process flow loss.",
    },
    {
      key: "runtime_hours",
      label: "Operating Hours",
      value: latest.runtime_hours,
      unit: "hrs",
      icon: Clock3,
      explanation: "Shows usage age and helps estimate wear, preventive replacement, and end-of-life risk.",
    },
  ];

  return definitions
    .filter((sensor): sensor is Omit<SensorCardModel, "status"> => typeof sensor.value === "number" && !Number.isNaN(sensor.value))
    .map((sensor) => ({
      ...sensor,
      status: getSensorStatus(sensor.key, sensor.value),
    }));
}

function getSensorStatus(key: keyof SensorLatestResponse, value: number): SensorStatus {
  if (key === "vibration") return value >= 9 ? "critical" : value >= 7 ? "warning" : "normal";
  if (key === "temperature") return value >= 90 ? "critical" : value >= 80 ? "warning" : "normal";
  if (key === "current_value") return value >= 190 ? "critical" : value >= 175 ? "warning" : "normal";
  if (key === "pressure") return value <= 3 ? "critical" : value <= 5 ? "warning" : "normal";
  if (key === "speed") return value <= 800 ? "critical" : value <= 1000 ? "warning" : "normal";
  if (key === "flow") return value <= 20 ? "critical" : value <= 35 ? "warning" : "normal";
  if (key === "runtime_hours") return value >= 7000 ? "warning" : "normal";
  return "normal";
}

function SensorCard({ sensor }: { sensor: SensorCardModel }) {
  const Icon = sensor.icon;
  return (
    <article className={`condition-sensor-card sensor-${sensor.status}`}>
      <div className="condition-sensor-heading">
        <div>
          <span>{sensor.label}</span>
          <strong>{formatNumber(sensor.value, sensor.key === "runtime_hours" ? 0 : 1)} <small>{sensor.unit}</small></strong>
        </div>
        <Icon size={22} />
      </div>
      <div className={`sensor-status-chip status-${sensor.status}`}>{sensor.status}</div>
      <p>{sensor.explanation}</p>
    </article>
  );
}

function SensorTrendPreview({ history }: { history: Array<Record<string, number | string | null | undefined>> }) {
  return (
    <section className="dark-panel">
      <h2>Sensor Trend Preview</h2>
      <p>Vibration, temperature, and flow trend from backend sensor history.</p>
      {history.length ? (
        <div className="dark-chart-box">
          <ResponsiveContainer width="100%" height={290}>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" stroke="#223653" />
              <XAxis dataKey="timestamp" stroke="#9fb2cc" hide />
              <YAxis stroke="#9fb2cc" />
              <Tooltip contentStyle={{ background: "#0b1b33", border: "1px solid #284463", color: "#eaf2ff" }} />
              <Line type="monotone" dataKey="vibration" stroke="#38bdf8" strokeWidth={2.5} dot={false} />
              <Line type="monotone" dataKey="temperature" stroke="#f59e0b" strokeWidth={2.5} dot={false} />
              <Line type="monotone" dataKey="flow" stroke="#22c55e" strokeWidth={2.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <EmptyState title="Trend data will appear when historical sensor data is available." message="The backend sensor history endpoint returned no points for this asset." />
      )}
    </section>
  );
}

function SensorAiInsight({
  asset,
  assetName,
  strongestSignal,
  status,
  onCreateNotification,
}: {
  asset?: AssetBasicResponse;
  assetName: string;
  strongestSignal?: SensorCardModel;
  status: string;
  onCreateNotification?: (draft: MaintenanceNotificationDraft) => void;
}) {
  const text = strongestSignal
    ? `${assetName} shows ${status} condition. The strongest signal is ${strongestSignal.label.toLowerCase()}. Possible issues include ${failureHint(strongestSignal.label)}.`
    : "I am still learning from the available sensor and maintenance data. I can help better when more history and feedback are available.";

  return (
    <section className="dark-panel ai-insight-panel">
      <div className="dark-panel-heading">
        <div>
          <h2>Current Sensor-Based AI Insight</h2>
          <p>This is a practical frontend summary of backend sensor data, not a separate ML decision.</p>
        </div>
        <AlertTriangle size={22} />
      </div>
      <p className="ai-insight-text">{text}</p>
      <div className="dark-fact-list">
        <div><span>Recommended check</span><strong>{strongestSignal ? recommendedCheck(strongestSignal.label) : "Capture more sensor history"}</strong></div>
        <div><span>Next step</span><strong>Compare this trend with maintenance history before creating the final work order.</strong></div>
      </div>
      <button
        className="primary-button"
        type="button"
        disabled={!asset}
        onClick={() =>
          asset &&
          onCreateNotification?.({
            asset_id: asset.asset_id,
            asset_code: asset.asset_code,
            asset_name: asset.asset_name,
            priority: strongestSignal?.status === "critical" ? "critical" : strongestSignal?.status === "warning" ? "high" : "medium",
            short_text: strongestSignal
              ? `${strongestSignal.label} abnormal on ${assetName}`
              : `${assetName} condition monitoring review`,
            description: text,
            failure_mode: strongestSignal ? failureHint(strongestSignal.label) : null,
            recommended_action: strongestSignal
              ? recommendedCheck(strongestSignal.label)
              : "Capture additional sensor history and inspect the asset.",
            source: "condition_monitoring",
            requested_by: "maintenance_manager",
          })
        }
      >
        <BellRing size={16} /> Create Notification
      </button>
    </section>
  );
}

function SensorMeaningTable() {
  const rows = [
    ["Vibration", "Increasing vibration or spikes", "Bearing wear, imbalance, misalignment, looseness", "Inspect bearing, alignment, mounting, gearbox"],
    ["Temperature", "Temperature rising above normal trend", "Overheating, friction, poor lubrication, overload", "Check lubrication, cooling, bearing friction"],
    ["Current Draw", "Current increasing while output stays same", "Motor overload, jam, mechanical resistance", "Check load, gearbox, belt, coupling, electrical phase"],
    ["Pressure", "Pressure too high or too low", "Blockage, leakage, valve or pneumatic issue", "Inspect valves, cylinders, filters, air leaks"],
    ["Speed", "Speed drops or fluctuates", "Drive issue, belt slip, overload, mechanical resistance", "Inspect drive, belt, gearbox, load"],
    ["Flow", "Flow drops below expected level", "Blockage, leakage, pump degradation", "Check filters, valves, pump, leakage"],
    ["Operating Hours", "Running beyond expected interval", "Age-related wear, end-of-life risk", "Plan preventive replacement or inspection"],
  ];

  return (
    <section className="dark-panel">
      <h2>What Each Sensor Can Predict</h2>
      <div className="table-scroll">
        <table className="dark-table">
          <thead>
            <tr>
              <th>Sensor</th>
              <th>Abnormal Pattern</th>
              <th>Possible Failure</th>
              <th>Typical Action</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([sensor, pattern, failure, action]) => (
              <tr key={sensor}>
                <td>{sensor}</td>
                <td>{pattern}</td>
                <td>{failure}</td>
                <td>{action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function DarkInfoCard({ icon: Icon, label, value, note, tone = "info" }: { icon: typeof Activity; label: string; value: string; note: string; tone?: "good" | "warning" | "critical" | "info" }) {
  return (
    <article className={`dark-info-card tone-${tone}`}>
      <Icon size={22} />
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <p>{note}</p>
      </div>
    </article>
  );
}

function sensorWeight(status: SensorStatus): number {
  return status === "critical" ? 3 : status === "warning" ? 2 : 1;
}

function statusTone(value: string | null | undefined): "good" | "warning" | "critical" | "info" {
  const normalized = String(value || "").toLowerCase();
  if (normalized.includes("critical")) return "critical";
  if (normalized.includes("warning") || normalized.includes("attention") || normalized.includes("medium") || normalized.includes("high")) return "warning";
  if (normalized.includes("healthy") || normalized.includes("low")) return "good";
  return "info";
}

function failureHint(sensorLabel: string): string {
  if (sensorLabel === "Vibration") return "bearing wear, misalignment, imbalance, or mechanical looseness";
  if (sensorLabel === "Temperature") return "overheating, friction, poor lubrication, cooling problems, or overload";
  if (sensorLabel === "Current Draw") return "motor overload, mechanical resistance, or jams";
  if (sensorLabel === "Pressure") return "air leakage, valve restriction, blockage, or pneumatic instability";
  if (sensorLabel === "Speed") return "drive slip, overload, resistance, or process instability";
  if (sensorLabel === "Flow") return "blockage, leakage, valve restriction, or pump degradation";
  return "age-related wear or end-of-life risk";
}

function recommendedCheck(sensorLabel: string): string {
  if (sensorLabel === "Vibration") return "Inspect bearings, alignment, mounting, and gearbox condition.";
  if (sensorLabel === "Temperature") return "Check lubrication, cooling, and bearing friction.";
  if (sensorLabel === "Current Draw") return "Check motor load, gearbox, belt, coupling, and phase balance.";
  if (sensorLabel === "Pressure") return "Inspect valves, cylinders, filters, and air leaks.";
  if (sensorLabel === "Speed") return "Inspect drive, belt, gearbox, and load.";
  if (sensorLabel === "Flow") return "Check filters, valves, pump, and leakage points.";
  return "Review preventive replacement interval and inspection history.";
}

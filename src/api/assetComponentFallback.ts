import type {
  AssetComponent,
  AssetComponentsResponse,
  ComponentDetailResponse,
  ComponentMaintenanceHistory,
  ComponentUpcomingTask,
} from "../types/assetComponent";

const fallbackComponents: Record<number, AssetComponent[]> = {
  1: [
    component(101, 1, "FUR-BURNER", "Burner System", "Thermal control", true, true, "condition based monitoring plus weekly combustion inspection", 14, "flame instability;nozzle fouling", "Verify combustion trend and inspect burner nozzles", "critical", "healthy", 91),
    component(102, 1, "FUR-REFRACTORY", "Refractory Lining", "Maintainable lining", false, false, "inspection based maintenance during planned shutdown", 180, "cracking;hot spots", "Inspect refractory during next scheduled furnace window", "critical", "healthy", 86),
    component(103, 1, "FUR-TEMP", "Temperature Control System", "Instrumentation", true, true, "calibration and trend monitoring", 30, "sensor drift;controller alarm", "Validate temperature loop and calibrate thermocouples", "critical", "healthy", 93),
    component(104, 1, "FUR-COOLING", "Cooling System", "Utilities", true, true, "flow and temperature monitoring", 30, "low flow;blocked strainer", "Check cooling flow and clean strainers", "high", "healthy", 88),
    component(105, 1, "FUR-EXHAUST", "Exhaust System", "Air handling", true, true, "draft monitoring and monthly inspection", 30, "draft instability;damper sticking", "Inspect damper response and exhaust draft", "high", "healthy", 84),
    component(106, 1, "FUR-SAFETY", "Safety Interlocks", "Safety", false, false, "proof test and functional safety inspection", 90, "interlock trip;limit switch fault", "Perform scheduled safety interlock proof test", "critical", "healthy", 96),
  ],
  2: [
    component(201, 2, "FDR-BOWL", "Feeder Bowl", "Process contact", false, false, "visual inspection and wear check", 30, "wear buildup;thermal cracking", "Inspect bowl wear and remove buildup", "high", "healthy", 87),
    component(202, 2, "FDR-MOTOR", "Drive Motor", "Rotating equipment", true, true, "vibration and current monitoring", 30, "bearing wear;overload", "Trend motor current and inspect bearings", "high", "healthy", 89),
    component(203, 2, "FDR-BELT", "Belt/Chain Drive", "Mechanical drive", true, true, "condition monitoring and tension inspection", 30, "chain slack;misalignment", "Check drive tension and alignment", "medium", "healthy", 85),
    component(204, 2, "FDR-HOPPER", "Hopper", "Material handling", false, false, "cleaning and blockage inspection", 14, "bridging;material blockage", "Inspect hopper throat and clean buildup", "medium", "healthy", 82),
    component(205, 2, "FDR-GATE", "Flow Control Gate", "Flow control", true, true, "flow trend and weekly actuation check", 14, "sticking gate;low flow", "Check gate movement and verify flow response", "high", "attention", 78),
    component(206, 2, "FDR-VIBRATION", "Vibration Unit", "Mechanical assist", true, true, "vibration monitoring and mounting inspection", 30, "loose mounting;unbalanced motion", "Inspect vibration mounts and trend amplitude", "medium", "healthy", 86),
  ],
  3: [
    component(301, 3, "ISM-MOLDS", "Molds", "Tooling", false, false, "preventive replacement and dimensional inspection", 90, "wear marks;neck finish defect;surface checking", "Review replacement timing and inspect mold wear pattern", "critical", "attention", null, "Blank and blow molds for bottle forming"),
    component(302, 3, "ISM-BLANK", "Blank Side Mechanism", "Mechanism", true, true, "condition monitoring and weekly mechanical inspection", 14, "sticking motion;timing drift", "Inspect blank side motion and verify section timing", "critical", "attention", 66),
    component(303, 3, "ISM-BLOW", "Blow Side Mechanism", "Mechanism", true, true, "condition monitoring and weekly mechanical inspection", 14, "mechanical looseness;timing drift", "Inspect blow side linkage and verify final blow timing", "critical", "attention", 69),
    component(304, 3, "ISM-PNEUMATIC", "Pneumatic System", "Utilities", true, true, "pressure monitoring and leak inspection", 14, "air leak;low pressure;valve sticking", "Inspect air leaks and validate valve response", "critical", "warning", 61),
    component(305, 3, "ISM-LUBE", "Lubrication System", "Lubrication", true, true, "oil pressure monitoring and lubrication route check", 7, "blocked line;low lubrication;contamination", "Check lubrication flow and clean blocked line", "critical", "warning", 64),
    component(306, 3, "ISM-COOLING", "Cooling System", "Utilities", true, true, "flow monitoring and weekly cleaning", 14, "low flow;blocked nozzle", "Inspect cooling nozzles and flow balance", "high", "attention", 72),
    component(307, 3, "ISM-PUSHOUT", "Pushout System", "Mechanism", true, true, "timing inspection and drive monitoring", 21, "pushout timing fault;mechanical wear", "Verify pushout timing and inspect pivots", "high", "attention", 70),
    component(308, 3, "ISM-DRIP", "Drip Deflector", "Tooling", false, false, "visual inspection and cleaning", 14, "contamination;bent deflector", "Inspect deflector position and clean deposits", "medium", "healthy", null),
    component(309, 3, "ISM-SHEAR", "Shear Mechanism", "Cutting mechanism", true, true, "vibration current and blade inspection", 14, "blade wear;timing drift", "Inspect shear blades and verify timing", "critical", "attention", 67),
    component(310, 3, "ISM-CONTROL", "Control Panel", "Electrical control", true, true, "electrical inspection and alarm review", 30, "drive fault;loose terminal", "Review control alarms and inspect cabinet cooling", "critical", "healthy", 82),
  ],
  4: [
    component(401, 4, "LEHR-DRIVE", "Lehr Drive System", "Drive system", true, true, "vibration and speed monitoring", 30, "gearbox resistance;drive fault", "Trend drive current and inspect gearbox", "high", "healthy", 85),
    component(402, 4, "LEHR-FANS", "Cooling Zone Fans", "Air handling", true, true, "temperature and vibration monitoring", 30, "bearing noise;low airflow", "Inspect fan bearings and airflow balance", "high", "healthy", 83),
    component(403, 4, "LEHR-TEMP", "Temperature Control System", "Instrumentation", true, true, "calibration and zone trend review", 30, "sensor drift;zone deviation", "Calibrate zone sensors and verify profile", "critical", "healthy", 87),
    component(404, 4, "LEHR-ROLLERS", "Roller System", "Material handling", false, false, "inspection and replacement by wear condition", 60, "roller wear;skewed travel", "Inspect roller wear and alignment", "high", "healthy", 82),
    component(405, 4, "LEHR-CHAIN", "Conveyor Chain", "Mechanical transport", true, true, "tension inspection and drive monitoring", 30, "chain slack;guide wear", "Check chain tension and guide wear", "high", "attention", 76),
    component(406, 4, "LEHR-HEATING", "Burner/Heating Zone", "Thermal control", true, true, "combustion and temperature monitoring", 30, "burner fault;zone instability", "Inspect heating zone stability and burner response", "critical", "healthy", 88),
  ],
  5: [
    component(501, 5, "INSP-CAMERA", "Camera System", "Vision system", true, true, "image quality monitoring and cleaning", 14, "dirty lens;camera fault", "Clean lenses and verify image quality", "high", "healthy", 78),
    component(502, 5, "INSP-LIGHTING", "Lighting Unit", "Vision support", true, true, "intensity check and cleaning", 14, "low intensity;strobe failure", "Check lighting intensity and replace weak strobe", "medium", "attention", 72),
    component(503, 5, "INSP-REJECT", "Rejection System", "Reject mechanism", true, true, "actuation timing check and air pressure monitoring", 14, "reject timing fault;air leak", "Verify reject timing and pneumatic response", "high", "attention", 70),
    component(504, 5, "INSP-CONVEYOR", "Bottle Handling Conveyor", "Material handling", true, true, "speed monitoring and alignment inspection", 30, "tracking issue;belt wear", "Inspect guide rails and conveyor tracking", "high", "healthy", 80),
    component(505, 5, "INSP-SENSORS", "Sensor Array", "Instrumentation", true, true, "trigger validation and cleaning", 14, "false rejects;sensor contamination", "Clean sensors and validate trigger timing", "high", "attention", 73),
    component(506, 5, "INSP-CONTROL", "Control Panel", "Electrical control", true, true, "alarm review and electrical inspection", 30, "drive alarm;network fault", "Review alarms and inspect cabinet cooling", "high", "healthy", 82),
  ],
  6: [
    component(601, 6, "PKG-CASE-PACKER", "Case Packer", "Packaging module", true, true, "current and cycle monitoring plus weekly inspection", 21, "jam;case feed fault", "Inspect case feed and cycle timing", "high", "attention", 74),
    component(602, 6, "PKG-WRAP", "Wrap Around Packer", "Packaging module", true, true, "temperature and cycle monitoring", 21, "miswrap;adhesive issue", "Verify wrap timing and adhesive temperature", "high", "attention", 73),
    component(603, 6, "PKG-STRAP", "Strapping System", "Packaging module", true, true, "tension check and cycle monitoring", 30, "low strap tension;seal fault", "Check strap tension and sealing head wear", "medium", "healthy", 80),
    component(604, 6, "PKG-LABEL", "Labeling System", "Packaging module", true, true, "print quality check and sensor cleaning", 30, "label skew;printer fault", "Verify label alignment and clean sensors", "medium", "healthy", 82),
    component(605, 6, "PKG-SUCTION", "Vacuum Suction Cups", "Maintainable wear item", false, false, "preventive replacement by cycle count and visual inspection", 30, "vacuum loss;worn cups;missed pickup", "Replace suction cups and inspect vacuum line", "high", "warning", null, "Suction cups used for pickup and placement"),
    component(606, 6, "PKG-SEAL", "Seal Kit", "Maintainable wear item", false, false, "preventive replacement every 45 days", 45, "seal wear;vacuum leakage", "Inspect seal kit and replace if leakage continues", "high", "attention", null),
    component(607, 6, "PKG-ALIGN", "Conveyor Belt Alignment", "Mechanical alignment", true, true, "tracking inspection and motor current monitoring", 21, "belt drift;guide wear", "Adjust belt tracking and inspect guide wear", "medium", "attention", 76),
    component(608, 6, "PKG-PNEUMATIC", "Pneumatic System", "Utilities", true, true, "pressure monitoring and leak inspection", 14, "air leak;low pressure;slow cylinder", "Inspect pneumatic leaks and validate cylinder speed", "high", "attention", 71),
    component(609, 6, "PKG-SAFETY", "Safety Guards", "Safety", false, false, "functional safety proof test", 90, "guard switch fault;light curtain trip", "Complete safety device proof test on schedule", "critical", "healthy", 95),
  ],
};

const fallbackHistory: ComponentMaintenanceHistory[] = [
  history(301, "2026-04-18", "WO-ISM-0418", "Molds replaced due to bottle defects", "mold wear", "Replaced blank and blow molds", "mold set", 2.5, "Wear pattern found on neck finish area"),
  history(301, "2026-03-05", "WO-ISM-0305", "Mold inspection found neck finish defect", "surface checking", "Replaced worn mold insert", "mold insert", 1.2, "Review interval after next campaign"),
  history(304, "2026-05-03", "WO-ISM-0503", "Pressure drop on section manifold", "pneumatic leak", "Repaired leaking valve block", "valve seal", 1.4, "Leak check improved response"),
  history(305, "2026-04-22", "WO-ISM-0422", "Temperature increase on forming section", "blocked lubrication line", "Cleaned lube line and verified flow", "oil filter", 0.9, "Monitor lube alarms"),
  history(309, "2026-04-14", "WO-ISM-0414", "Shear timing drift", "blade wear", "Replaced shear blades and adjusted timing", "shear blades", 1.8, "Timing stable after adjustment"),
  history(605, "2026-05-02", "WO-PKG-0502", "Vacuum loss caused missed pickup", "worn suction cups", "Replaced suction cups", "suction cups", 1.1, "Cycle count exceeded normal wear interval"),
  history(605, "2026-04-01", "WO-PKG-0401", "Repeated pickup misses", "vacuum leakage", "Inspected vacuum line and replaced cups", "suction cups", 1.3, "Consider shorter interval if repeats continue"),
  history(606, "2026-04-20", "WO-PKG-0420", "Sealing failure during package run", "seal wear", "Replaced seal kit", "seal kit", 1.6, "Seal wear visible at inspection"),
  history(601, "2026-05-08", "WO-PKG-0508", "Repeated case jams", "alignment drift", "Corrected case packer alignment", "guide rail", 1.0, "Jams reduced after alignment"),
  history(603, "2026-04-26", "WO-PKG-0426", "Loose straps", "low strap tension", "Adjusted strapping tension", "strap tensioner", 0.7, "Recheck tension next shift"),
];

const fallbackTasks: ComponentUpcomingTask[] = [
  task(301, 3, "ISM-MOLDS", "Replace mold set", "2026-06-03", "quarterly", 90, "critical", "due_soon", "preventive replacement and dimensional inspection", "2026-05-30", "Sample history shows mold wear can create bottle defects before the planned date."),
  task(304, 3, "ISM-PNEUMATIC", "Inspect pneumatic valves and air leaks", "2026-05-21", "biweekly", 14, "high", "due_soon", "pressure monitoring and leak inspection", "2026-05-20", "Recent leak history makes the next inspection important."),
  task(305, 3, "ISM-LUBE", "Check lubrication system", "2026-05-18", "weekly", 7, "high", "overdue", "oil pressure monitoring and lubrication route check", "2026-05-18", "Lubrication restrictions can increase temperature and wear."),
  task(605, 6, "PKG-SUCTION", "Replace vacuum suction cups", "2026-06-01", "monthly", 30, "high", "due_soon", "preventive replacement by cycle count and visual inspection", "2026-05-29", "Vacuum loss has repeated when suction cups exceed the normal interval."),
  task(606, 6, "PKG-SEAL", "Replace seal kit", "2026-06-04", "45 days", 45, "high", "planned", "preventive replacement every 45 days", "2026-06-01", "Seal wear has caused previous vacuum leakage."),
  task(608, 6, "PKG-PNEUMATIC", "Inspect pneumatic lines", "2026-05-21", "biweekly", 14, "medium", "due_soon", "pressure monitoring and leak inspection", "2026-05-21", "Slow cylinders and low pressure should be checked before production."),
];

export function getFallbackAssetComponents(assetId: number | string): AssetComponentsResponse | null {
  const normalizedAssetId = Number(assetId);
  const components = fallbackComponents[normalizedAssetId];
  if (!components) return null;
  return { asset_id: normalizedAssetId, components };
}

export function getFallbackComponentDetail(
  assetId: number | string,
  componentId: number | string,
): ComponentDetailResponse | null {
  const normalizedAssetId = Number(assetId);
  const normalizedComponentId = Number(componentId);
  const component = fallbackComponents[normalizedAssetId]?.find((item) => item.component_id === normalizedComponentId);
  if (!component) return null;

  const maintenanceHistory = fallbackHistory.filter((item) => item.component_id === component.component_id);
  const upcomingTasks = fallbackTasks.filter((item) => item.component_id === component.component_id);

  return {
    component,
    maintenance_history: maintenanceHistory,
    upcoming_tasks: upcomingTasks,
    frequent_failures: component.frequent_failures,
    ai_recommendation: buildFallbackRecommendation(component, maintenanceHistory, upcomingTasks),
    sensor_summary: component.has_sensor_data || component.has_cbm ? { cbm_status: "Condition monitoring available" } : null,
    strategy_assessment: component.has_sensor_data || component.has_cbm
      ? "Condition monitoring is available. Review sensor trends together with work orders and feedback."
      : "AI learning status: more maintenance history and technician feedback will help optimize this maintenance interval.",
  };
}

function component(
  component_id: number,
  asset_id: number,
  component_code: string,
  component_name: string,
  component_type: string,
  has_sensor_data: boolean,
  has_cbm: boolean,
  maintenance_strategy: string,
  maintenance_interval_days: number,
  frequentFailures: string,
  recommended_action: string,
  criticality = "high",
  condition = "healthy",
  health_score: number | null = 80,
  description = `${component_name} maintainable item`,
): AssetComponent {
  return {
    component_id,
    asset_id,
    component_code,
    component_name,
    component_type,
    description,
    criticality,
    condition,
    health_score,
    has_sensor_data,
    has_cbm,
    maintenance_strategy,
    maintenance_interval_days,
    last_maintenance_date: "2026-05-02",
    next_planned_maintenance: asset_id === 3 ? "2026-06-03" : "2026-06-01",
    frequent_failures: frequentFailures.split(";").filter(Boolean),
    recommended_action,
  };
}

function history(
  component_id: number,
  date: string,
  work_order_id: string,
  failure_description: string,
  failure_cause: string,
  action_taken: string,
  replaced_part: string,
  downtime_hours: number,
  technician_note: string,
): ComponentMaintenanceHistory {
  return {
    history_id: Number(`${component_id}${date.replace(/-/g, "").slice(4)}`),
    component_id,
    date,
    work_order_id,
    failure_description,
    failure_cause,
    action_taken,
    replaced_part,
    downtime_hours,
    technician_note,
  };
}

function task(
  component_id: number,
  asset_id: number,
  component_code: string,
  task_name: string,
  planned_date: string,
  frequency: string,
  recommended_interval_days: number,
  priority: string,
  status: string,
  maintenance_strategy: string,
  ai_recommended_date: string,
  ai_reason: string,
): ComponentUpcomingTask {
  return {
    schedule_id: Number(`${component_id}${planned_date.replace(/-/g, "").slice(4)}`),
    component_id,
    asset_id,
    component_code,
    task_name,
    planned_date,
    frequency,
    last_completed_date: "2026-05-02",
    recommended_interval_days,
    priority,
    status,
    maintenance_strategy,
    ai_recommended_date,
    ai_reason,
  };
}

function buildFallbackRecommendation(
  component: AssetComponent,
  maintenanceHistory: ComponentMaintenanceHistory[],
  upcomingTasks: ComponentUpcomingTask[],
): string {
  const task = upcomingTasks[0];
  const historyNote = maintenanceHistory.length
    ? "Sample maintenance history is available for this component."
    : "More maintenance history and technician feedback will improve this recommendation.";
  const taskNote = task ? `Next task: ${task.task_name} on ${task.planned_date}.` : "No upcoming task is available in fallback data.";

  if (component.has_sensor_data || component.has_cbm) {
    return `${component.recommended_action || "Review component condition."} Condition monitoring is available. ${historyNote} ${taskNote}`;
  }

  return `${component.recommended_action || "Review maintenance interval."} No direct sensor data is available, so use strategy, history, inspection results, and feedback. ${historyNote} ${taskNote}`;
}

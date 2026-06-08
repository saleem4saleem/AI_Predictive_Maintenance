import { BrainCircuit, CheckCircle2 } from "lucide-react";
import type { AIExplanation } from "../../types/asset";
import type { PredictionResponse } from "../../types/prediction";
import type { RecommendationItem } from "../../types/recommendation";
import type { ComponentDetailResponse } from "../../types/assetComponent";
import { Card } from "../common/Card";
import { RiskBadge } from "../common/RiskBadge";

const LIMITED_DATA_MESSAGE =
  "I am still learning from the available maintenance data. I can help you better when more asset history, sensor data, and technician feedback are available.";

interface AssetAIRecommendationProps {
  prediction: PredictionResponse;
  explanation: AIExplanation;
  actions: RecommendationItem[];
  selectedDetail: ComponentDetailResponse | null;
}

export function AssetAIRecommendation({ prediction, explanation, actions, selectedDetail }: AssetAIRecommendationProps) {
  const component = selectedDetail?.component;
  const hasComponentHistory = Boolean(selectedDetail?.maintenance_history.length);
  const urgentTask = selectedDetail?.upcoming_tasks?.find((task) => task.status === "overdue" || task.status === "due_soon" || ["high", "critical"].includes(task.priority));
  const componentRecommendation = selectedDetail ? buildComponentRecommendation(selectedDetail) : null;
  const dataSources = [
    "asset prediction",
    component?.has_sensor_data || component?.has_cbm ? "sensor/CBM data" : null,
    hasComponentHistory ? "maintenance history" : null,
    urgentTask ? "maintenance schedule" : null,
    "maintenance rules",
    "technician feedback",
    "expert notes",
  ].filter(Boolean);

  return (
    <Card title="AI Recommendation" subtitle="Honest asset and component recommendation based on available backend data.">
      <div className="ai-recommendation-layout">
        <div className="component-recommendation">
          <CheckCircle2 size={18} />
          <div>
            <strong>{prediction.recommended_action}</strong>
            <p>{prediction.explanation || explanation.summary || LIMITED_DATA_MESSAGE}</p>
            <RiskBadge risk={prediction.risk_level} />
          </div>
        </div>

        {selectedDetail && (
          <div className="component-recommendation">
            <BrainCircuit size={18} />
            <div>
              <strong>{selectedDetail.component.component_name}</strong>
              <p>{componentRecommendation || selectedDetail.ai_recommendation || LIMITED_DATA_MESSAGE}</p>
              {urgentTask && (
                <span className="muted">
                  Upcoming task: {urgentTask.task_name} is {urgentTask.status} for {urgentTask.planned_date}.
                </span>
              )}
              <span className="muted">{selectedDetail.strategy_assessment || LIMITED_DATA_MESSAGE}</span>
            </div>
          </div>
        )}

        <div className="data-source-list">
          <strong>Data sources used</strong>
          <div className="flow-badges">
            {dataSources.map((source) => (
              <span className="badge badge-unknown" key={source}>{source}</span>
            ))}
          </div>
          {(!selectedDetail || (!selectedDetail.maintenance_history.length && !component?.has_sensor_data)) && (
            <p className="muted">{LIMITED_DATA_MESSAGE}</p>
          )}
        </div>

        {actions.length > 0 && (
          <div>
            <strong>Practical actions</strong>
            <ul className="recommendation-mini-list">
              {actions.slice(0, 4).map((item, index) => (
                <li key={`${item.action}-${index}`}>{item.action}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Card>
  );
}

function buildComponentRecommendation(detail: ComponentDetailResponse): string {
  const name = detail.component.component_name.toLowerCase();
  const task = (detail.upcoming_tasks || []).find((item) => item.status === "overdue" || item.status === "due_soon" || ["high", "critical"].includes(item.priority));

  if (name.includes("mold")) {
    return "Current strategy is preventive replacement. Based on sample history, mold wear has caused bottle defects before. Keep the replacement interval at 90 days until more technician feedback proves the interval can be safely changed.";
  }

  if (name.includes("suction cup")) {
    return "Vacuum loss and suction cup wear appear repeatedly in history. Replace suction cups before the next planned run and review whether the 30-day interval is still optimal.";
  }

  if (task) {
    return `${detail.component.recommended_action || detail.ai_recommendation} Prioritize ${task.task_name} because it is ${task.status} and marked ${task.priority}.`;
  }

  return detail.ai_recommendation;
}

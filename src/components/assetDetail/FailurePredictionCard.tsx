import type { PredictionResponse } from "../../types/prediction";
import { formatDate } from "../../utils/date";
import { formatPercent, titleCase } from "../../utils/formatters";
import { Card } from "../common/Card";
import { RiskBadge } from "../common/RiskBadge";

export function FailurePredictionCard({ prediction }: { prediction: PredictionResponse }) {
  return (
    <Card title="Failure Prediction" subtitle="Backend prediction contract">
      <div className="prediction-grid">
        <div>
          <span>7 day probability</span>
          <strong>{formatPercent(prediction.failure_probability_7_days)}</strong>
        </div>
        <div>
          <span>30 day probability</span>
          <strong>{formatPercent(prediction.failure_probability_30_days)}</strong>
        </div>
        <div>
          <span>Predicted date</span>
          <strong>{formatDate(prediction.predicted_failure_date)}</strong>
        </div>
        <div>
          <span>Remaining useful life</span>
          <strong>{prediction.remaining_useful_life_days ?? "Not available"} days</strong>
        </div>
      </div>
      <div className="card-divider" />
      <div className="split-row">
        <RiskBadge risk={prediction.risk_level} />
        <span>Confidence: {titleCase(prediction.confidence)}</span>
      </div>
      <p className="muted">Likely failure mode: {titleCase(prediction.predicted_failure_mode || "not available")}</p>
      <p className="muted">Model version: {prediction.model_version}</p>
    </Card>
  );
}

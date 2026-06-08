import type { CSSProperties } from "react";
import { healthClass } from "../../utils/status";

export function HealthScoreGauge({ score }: { score: number }) {
  return (
    <div className={`health-gauge gauge-${healthClass(score)}`} style={{ "--score": `${score * 3.6}deg` } as CSSProperties}>
      <div>
        <strong>{score.toFixed(0)}</strong>
        <span>Health Score</span>
      </div>
    </div>
  );
}

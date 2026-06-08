import { Bot } from "lucide-react";
import type { AIExplanation } from "../../types/asset";
import { Card } from "../common/Card";

export function AIExplanationPanel({ explanation }: { explanation: AIExplanation }) {
  return (
    <Card title="AI Explanation" subtitle="Explanation layer only; backend logic decides risk.">
      <div className="ai-panel">
        <Bot size={24} />
        <div>
          <p>{explanation.summary}</p>
          <span>Confidence: {explanation.confidence} · Fallback used: {explanation.fallback_used ? "Yes" : "No"}</span>
        </div>
      </div>
    </Card>
  );
}

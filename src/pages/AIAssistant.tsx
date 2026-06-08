import { Bot, SendHorizonal, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";
import { Card } from "../components/common/Card";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingSkeleton } from "../components/common/LoadingSkeleton";
import { PageHeader } from "../components/layout/PageHeader";
import { useAIAssistant } from "../hooks/useAIAssistant";
import { useAssetDetail } from "../hooks/useAssetDetail";
import type { AssetBasicResponse, AssetDetailResponse } from "../types/asset";
import { formatDate } from "../utils/date";
import { formatNumber, formatPercent, formatValue, titleCase } from "../utils/formatters";
import { getProductionAssetDisplayName } from "../utils/assetImageMap";

interface AIAssistantProps {
  assetId: number;
  assets: AssetBasicResponse[];
  onSelectAsset: (assetId: number) => void;
}

export function AIAssistant({ assetId, assets, onSelectAsset }: AIAssistantProps) {
  const detail = useAssetDetail(assetId);
  const context = useMemo(() => buildAssistantContext(detail.data), [detail.data]);
  const assistant = useAIAssistant(assetId, context);
  const [message, setMessage] = useState("");

  function sendCurrentMessage() {
    const text = message.trim();
    if (!text || assistant.loading) return;
    setMessage("");
    void assistant.sendMessage(text);
  }

  function sendSuggestion(question: string) {
    if (assistant.loading) return;
    void assistant.sendMessage(question);
  }

  return (
    <div className="page-stack">
      <PageHeader
        title="AI Assistant"
        description="Ask maintenance questions using the selected asset context from backend API data."
        actions={
          <label className="asset-select compact-select">
            Selected asset
            <select value={assetId} onChange={(event) => onSelectAsset(Number(event.target.value))}>
              {assets.map((asset) => (
                <option key={asset.asset_id} value={asset.asset_id}>
                  {getProductionAssetDisplayName(asset)}
                </option>
              ))}
            </select>
          </label>
        }
      />

      {detail.loading ? (
        <LoadingSkeleton rows={5} />
      ) : detail.error || !detail.data ? (
        <ErrorState message={detail.error || "Selected asset context is temporarily unavailable."} onRetry={detail.refresh} />
      ) : (
        <div className="assistant-layout">
          <section className="chat-panel ui-card">
            <div className="assistant-panel-heading">
              <div>
                <span className="eyebrow">Maintenance manager assistant</span>
                <h2>{getProductionAssetDisplayName(detail.data.asset)}</h2>
              </div>
              <Bot size={24} />
            </div>

            <div className="suggestion-grid">
              {assistant.suggestions.map((question) => (
                <button className="suggestion-chip" key={question} type="button" onClick={() => sendSuggestion(question)}>
                  {question}
                </button>
              ))}
            </div>

            <div className="chat-thread" aria-live="polite">
              {assistant.messages.map((chatMessage) => (
                <article className={`chat-message ${chatMessage.role}`} key={chatMessage.id}>
                  <span>{chatMessage.role === "user" ? "You" : "Assistant"}</span>
                  <p>{chatMessage.content}</p>
                </article>
              ))}
              {assistant.loading && (
                <article className="chat-message assistant">
                  <span>Assistant</span>
                  <p>Reviewing the available asset context...</p>
                </article>
              )}
            </div>

            {assistant.error && <p className="error-message">{assistant.error}</p>}

            <form
              className="chat-form"
              onSubmit={(event) => {
                event.preventDefault();
                sendCurrentMessage();
              }}
            >
              <textarea
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                placeholder="Ask about risk, shutdown checks, recommended actions, or missing data..."
              />
              <button className="primary-button" type="submit" disabled={assistant.loading || !message.trim()}>
                <SendHorizonal size={16} /> Send
              </button>
            </form>
          </section>

          <AssetContextPanel detail={detail.data} />
        </div>
      )}
    </div>
  );
}

function AssetContextPanel({ detail }: { detail: AssetDetailResponse }) {
  const prediction = detail.prediction;

  return (
    <aside className="assistant-context">
      <Card title="Selected Asset Context" subtitle="Data sent to the backend assistant request when available.">
        <div className="context-list">
          <ContextRow label="Asset" value={getProductionAssetDisplayName(detail.asset)} />
          <ContextRow label="Health score" value={`${formatNumber(prediction.health_score, 0)}%`} />
          <ContextRow label="Risk level" value={titleCase(prediction.risk_level)} />
          <ContextRow label="Condition" value={titleCase(prediction.condition)} />
          <ContextRow label="Predicted failure date" value={formatDate(prediction.predicted_failure_date)} />
          <ContextRow label="RUL" value={prediction.remaining_useful_life_days ? `${prediction.remaining_useful_life_days} days` : "Not available"} />
          <ContextRow label="7-day failure probability" value={formatPercent(prediction.failure_probability_7_days, 0)} />
          <ContextRow label="30-day failure probability" value={formatPercent(prediction.failure_probability_30_days, 0)} />
        </div>
      </Card>

      <Card title="Current Recommendation">
        <div className="ai-panel">
          <Sparkles size={22} />
          <div>
            <strong>{prediction.recommended_action}</strong>
            <p className="muted">{prediction.explanation}</p>
          </div>
        </div>
      </Card>

      <Card title="Similar Cases">
        {detail.similar_failures.length ? (
          <div className="case-list">
            {detail.similar_failures.slice(0, 3).map((item, index) => (
              <article className="case-item compact-case" key={`${item.title}-${index}`}>
                <span>{item.source_type}</span>
                <h3>{item.title}</h3>
                <p>{item.summary}</p>
              </article>
            ))}
          </div>
        ) : (
          <p className="muted">No similar historical cases found yet.</p>
        )}
      </Card>
    </aside>
  );
}

function ContextRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{formatValue(value)}</strong>
    </div>
  );
}

function buildAssistantContext(detail: AssetDetailResponse | null | undefined): Record<string, unknown> | null {
  if (!detail) return null;

  return {
    asset_name: getProductionAssetDisplayName(detail.asset),
    health_score: detail.prediction.health_score,
    risk_level: detail.prediction.risk_level,
    predicted_failure_date: detail.prediction.predicted_failure_date,
    remaining_useful_life_days: detail.prediction.remaining_useful_life_days,
    predicted_failure_mode: detail.prediction.predicted_failure_mode,
    sensor_summary: detail.sensor_summary,
    recommended_action: detail.prediction.recommended_action,
    recommended_actions: detail.recommended_actions.map((item) => item.action),
    similar_failures: detail.similar_failures.map((item) => `${item.title}: ${item.summary}`),
    maintenance_plan: detail.maintenance_plan,
  };
}

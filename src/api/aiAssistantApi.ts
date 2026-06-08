import { apiClient } from "./client";
import type { AIChatRequest, AIChatResponse } from "../types/aiAssistant";

export const aiAssistantFallbackMessage =
  "I am still learning from the available maintenance data. I can help you better when more asset history, sensor data, and technician feedback are available.";

export async function sendAIChatMessage(request: AIChatRequest): Promise<AIChatResponse> {
  try {
    const { data } = await apiClient.post<AIChatResponse>("/ai-assistant/chat", request);
    return data;
  } catch {
    return buildFallbackAnswer(request);
  }
}

function buildFallbackAnswer(request: AIChatRequest): AIChatResponse {
  const context = request.context || {};
  const message = request.message.toLowerCase();
  const assetName = stringValue(context.asset_name) || "this asset";
  const riskLevel = stringValue(context.risk_level);
  const healthScore = numberValue(context.health_score);
  const recommendedAction = stringValue(context.recommended_action);
  const predictedFailureDate = stringValue(context.predicted_failure_date);
  const remainingUsefulLifeDays = numberValue(context.remaining_useful_life_days);
  const similarFailures = Array.isArray(context.similar_failures)
    ? context.similar_failures.map((item) => String(item)).filter(Boolean).slice(0, 2)
    : [];

  if (!riskLevel && healthScore === null && !recommendedAction && similarFailures.length === 0) {
    return {
      answer: aiAssistantFallbackMessage,
      confidence: "low",
      fallback_used: true,
      suggestions: defaultSuggestions,
    };
  }

  if (message.includes("why") || message.includes("risk")) {
    return {
      answer: `${assetName} is currently shown as ${riskLevel || "unknown"} risk${healthScore !== null ? ` with a health score of ${healthScore}%` : ""}. The backend recommendation is: ${recommendedAction || "continue monitoring and validate the latest sensor trend"}.`,
      confidence: "medium",
      fallback_used: true,
      suggestions: defaultSuggestions,
    };
  }

  if (message.includes("shutdown") || message.includes("check") || message.includes("prioritize")) {
    return {
      answer: `For the next maintenance window, prioritize: ${recommendedAction || "inspect the selected asset, review open actions, and validate abnormal sensor behavior"}. ${remainingUsefulLifeDays !== null ? `The current remaining useful life estimate is ${remainingUsefulLifeDays} days.` : ""}`,
      confidence: "medium",
      fallback_used: true,
      suggestions: defaultSuggestions,
    };
  }

  if (message.includes("happened before") || message.includes("similar") || message.includes("history")) {
    return {
      answer: similarFailures.length
        ? `Similar available cases mention: ${similarFailures.join(" ")}`
        : aiAssistantFallbackMessage,
      confidence: similarFailures.length ? "medium" : "low",
      fallback_used: true,
      suggestions: defaultSuggestions,
    };
  }

  if (message.includes("planned") || message.includes("earlier")) {
    return {
      answer: predictedFailureDate
        ? `The predicted risk date is ${predictedFailureDate}. If this date is before the planned maintenance date, the maintenance planner should move the inspection earlier.`
        : aiAssistantFallbackMessage,
      confidence: predictedFailureDate ? "medium" : "low",
      fallback_used: true,
      suggestions: defaultSuggestions,
    };
  }

  if (message.includes("data") || message.includes("improve")) {
    return {
      answer: "More sensor history, SAP work orders, failure causes, action taken records, and technician feedback will improve prediction quality and recommendation confidence.",
      confidence: "medium",
      fallback_used: true,
      suggestions: defaultSuggestions,
    };
  }

  return {
    answer: aiAssistantFallbackMessage,
    confidence: "low",
    fallback_used: true,
    suggestions: defaultSuggestions,
  };
}

export const defaultSuggestions = [
  "Why is this asset at risk?",
  "What should I check during the next shutdown?",
  "What maintenance action should I prioritize?",
  "Has this failure happened before?",
  "Should I move the planned maintenance earlier?",
  "What data do you need to improve the prediction?",
];

function stringValue(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value : null;
}

function numberValue(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

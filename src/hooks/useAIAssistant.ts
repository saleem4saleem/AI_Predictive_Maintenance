import { useMemo, useState } from "react";
import { defaultSuggestions, sendAIChatMessage } from "../api/aiAssistantApi";
import { toApiError } from "../api/client";
import type { AIChatResponse, ChatMessage } from "../types/aiAssistant";

export function useAIAssistant(assetId: number | null, context: Record<string, unknown> | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "assistant-welcome",
      role: "assistant",
      content: "Ask me about asset risk, shutdown checks, maintenance timing, or what data would improve the prediction.",
      created_at: new Date().toISOString(),
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const suggestions = useMemo(() => defaultSuggestions, []);

  async function sendMessage(content: string): Promise<AIChatResponse | null> {
    const trimmed = content.trim();
    if (!trimmed) {
      return null;
    }

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmed,
      created_at: new Date().toISOString(),
    };

    setMessages((current) => [...current, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const response = await sendAIChatMessage({
        message: trimmed,
        asset_id: assetId,
        context,
      });

      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: response.answer,
        created_at: new Date().toISOString(),
      };

      setMessages((current) => [...current, assistantMessage]);
      return response;
    } catch (err) {
      setError(toApiError(err).message);
      return null;
    } finally {
      setLoading(false);
    }
  }

  return { messages, loading, error, suggestions, sendMessage };
}

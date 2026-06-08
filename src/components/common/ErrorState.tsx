import { AlertTriangle } from "lucide-react";

export function ErrorState({ message, onRetry, title }: { message: string; onRetry?: () => void; title?: string }) {
  const resolvedTitle = title || (message?.toLowerCase().includes("not found") ? "Endpoint was not found" : "Backend is not reachable");

  return (
    <div className="state-box state-error">
      <AlertTriangle size={24} />
      <h3>{resolvedTitle}</h3>
      <p>{message || "Backend is not reachable. Please check the API server."}</p>
      {onRetry && (
        <button className="secondary-button" type="button" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}

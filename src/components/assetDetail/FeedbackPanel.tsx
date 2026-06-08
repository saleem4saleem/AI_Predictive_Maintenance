import { useState, type FormEvent } from "react";
import { useFeedback } from "../../hooks/useFeedback";
import { Card } from "../common/Card";

export function FeedbackPanel({ assetId }: { assetId: number }) {
  const { data, loading, error, submit } = useFeedback();
  const [actualFailureMode, setActualFailureMode] = useState("");
  const [actionTaken, setActionTaken] = useState("");
  const [comment, setComment] = useState("");
  const [timing, setTiming] = useState<"too_early" | "correct" | "too_late" | "not_applicable">("correct");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await submit({
      asset_id: assetId,
      was_prediction_correct: true,
      actual_failure_happened: actualFailureMode.trim().length > 0,
      actual_failure_mode: actualFailureMode || null,
      action_taken: actionTaken || null,
      timing_feedback: timing,
      technician_comment: comment || null,
    });
  }

  return (
    <Card title="Technician Feedback" subtitle="Used later for retraining and recommendation improvement.">
      <form className="feedback-form" onSubmit={handleSubmit}>
        <label>
          Actual failure mode
          <input value={actualFailureMode} onChange={(event) => setActualFailureMode(event.target.value)} placeholder="e.g. suction cup wear" />
        </label>
        <label>
          Action taken
          <input value={actionTaken} onChange={(event) => setActionTaken(event.target.value)} placeholder="e.g. replaced suction cups" />
        </label>
        <label>
          Timing feedback
          <select value={timing} onChange={(event) => setTiming(event.target.value as typeof timing)}>
            <option value="correct">Correct</option>
            <option value="too_early">Too early</option>
            <option value="too_late">Too late</option>
            <option value="not_applicable">Not applicable</option>
          </select>
        </label>
        <label>
          Technician comment
          <textarea value={comment} onChange={(event) => setComment(event.target.value)} placeholder="What did you observe?" />
        </label>
        <button className="primary-button" disabled={loading} type="submit">
          {loading ? "Submitting..." : "Submit Feedback"}
        </button>
        {data && <p className="success-message">{data.message}</p>}
        {error && <p className="error-message">{error}</p>}
      </form>
    </Card>
  );
}

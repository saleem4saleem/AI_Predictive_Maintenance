import type { RagSearchResult } from "../../types/rag";
import { EmptyState } from "../common/EmptyState";
import { Card } from "../common/Card";

export function SimilarFailures({ failures }: { failures: RagSearchResult[] }) {
  return (
    <Card title="Similar Historical Failures">
      {failures.length === 0 ? (
        <EmptyState title="No similar historical cases found." message="Try searching the knowledge base for a broader symptom." />
      ) : (
        <div className="case-list">
          {failures.map((item, index) => (
            <article key={`${item.title}-${index}`} className="case-item">
              <span>{item.source_type}</span>
              <h3>{item.title}</h3>
              <p>{item.summary}</p>
              <small>Score {item.score?.toFixed(2) ?? "Not available"}</small>
            </article>
          ))}
        </div>
      )}
    </Card>
  );
}

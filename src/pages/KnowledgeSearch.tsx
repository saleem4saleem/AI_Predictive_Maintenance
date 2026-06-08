import { useState } from "react";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorState } from "../components/common/ErrorState";
import { Card } from "../components/common/Card";
import { PageHeader } from "../components/layout/PageHeader";
import { useRagSearch } from "../hooks/useRagSearch";

export function KnowledgeSearch({ assetId }: { assetId: number }) {
  const [query, setQuery] = useState("high vibration bearing failure");
  const { data, loading, error, search } = useRagSearch();

  return (
    <div className="page-stack">
      <PageHeader title="Knowledge Search" description="Search backend RAG fallback over expert notes, work orders, and checklists." />
      <Card>
        <form className="search-form" onSubmit={(event) => { event.preventDefault(); void search(query, assetId); }}>
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search similar failures..." />
          <button className="primary-button" type="submit" disabled={loading}>{loading ? "Searching..." : "Search"}</button>
        </form>
      </Card>
      {error && <ErrorState message={error} />}
      {data && (
        <Card title="Results">
          {data.results.length === 0 ? (
            <EmptyState title="No similar historical cases found." message="Try a broader symptom or another asset." />
          ) : (
            <div className="case-list">
              {data.results.map((item, index) => (
                <article className="case-item" key={`${item.title}-${index}`}>
                  <span>{item.source_type}</span>
                  <h3>{item.title}</h3>
                  <p>{item.summary}</p>
                  <small>Score {item.score?.toFixed(2) ?? "Not available"}</small>
                </article>
              ))}
            </div>
          )}
        </Card>
      )}
    </div>
  );
}

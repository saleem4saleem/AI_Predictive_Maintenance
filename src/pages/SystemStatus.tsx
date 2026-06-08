import { Card } from "../components/common/Card";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingSkeleton } from "../components/common/LoadingSkeleton";
import { PageHeader } from "../components/layout/PageHeader";
import { useHealthCheck } from "../hooks/useHealthCheck";
import { useAsyncData } from "../hooks/useAsyncData";
import { getActiveModel } from "../api/modelApi";

export function SystemStatus() {
  const health = useHealthCheck();
  const model = useAsyncData(getActiveModel, []);

  if (health.loading || model.loading) return <LoadingSkeleton rows={6} />;
  if (health.error || !health.data) return <ErrorState message={health.error || "Backend is not reachable. Please check the API server."} onRetry={health.refresh} />;

  return (
    <div className="page-stack">
      <PageHeader title="System Status" description="Operational status for backend, database, model registry, and active model contract." />
      <div className="detail-grid">
        <Card title="Backend Health">
          <pre>{JSON.stringify(health.data.health.data, null, 2)}</pre>
        </Card>
        <Card title="Database Health">
          <pre>{JSON.stringify(health.data.database.data, null, 2)}</pre>
        </Card>
        <Card title="Model Health">
          <pre>{JSON.stringify(health.data.model.data, null, 2)}</pre>
        </Card>
      </div>
      <Card title="Active Model">
        <pre>{JSON.stringify(model.data, null, 2)}</pre>
      </Card>
    </div>
  );
}

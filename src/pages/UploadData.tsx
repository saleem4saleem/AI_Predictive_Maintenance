import { UploadCloud } from "lucide-react";
import { Card } from "../components/common/Card";
import { PageHeader } from "../components/layout/PageHeader";

export function UploadData() {
  return (
    <div className="page-stack">
      <PageHeader title="Upload Data" description="SAP, alarm, checklist, and sensor upload UI placeholder until a backend upload endpoint is available." />
      <Card>
        <div className="state-box">
          <UploadCloud size={28} />
          <h3>Upload endpoint not available yet</h3>
          <p>When the backend exposes an upload route, this page can connect through the API layer without changing other pages.</p>
        </div>
      </Card>
    </div>
  );
}

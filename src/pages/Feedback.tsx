import { FeedbackPanel } from "../components/assetDetail/FeedbackPanel";
import { PageHeader } from "../components/layout/PageHeader";

export function Feedback({ assetId }: { assetId: number }) {
  return (
    <div className="page-stack">
      <PageHeader title="Feedback" description="Capture technician validation so backend feedback learning can improve future models." />
      <FeedbackPanel assetId={assetId} />
    </div>
  );
}

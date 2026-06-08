import {
  BellRing,
  CheckCircle2,
  ClipboardCheck,
  ExternalLink,
  Eye,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import { useState } from "react";
import type { ReactNode } from "react";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingSkeleton } from "../components/common/LoadingSkeleton";
import { PageHeader } from "../components/layout/PageHeader";
import { toApiError } from "../api/client";
import { useNotificationProposals } from "../hooks/useNotificationProposals";
import type {
  NotificationProposal,
  SAPNotificationFormPayload,
  SAPNotificationResponse,
} from "../types/notificationProposal";
import { formatDateTime } from "../utils/date";
import { formatNumber, formatPercent, titleCase } from "../utils/formatters";

type ModalMode = "approve" | "reject" | "sap-preview" | null;
const SAP_PORTAL_URL = import.meta.env.VITE_SAP_PORTAL_URL || "";

export function Notifications() {
  const proposals = useNotificationProposals();
  const [selectedProposal, setSelectedProposal] = useState<NotificationProposal | null>(null);
  const [modalMode, setModalMode] = useState<ModalMode>(null);
  const [reviewerName, setReviewerName] = useState("Maintenance Manager");
  const [comments, setComments] = useState("");
  const [reason, setReason] = useState("");
  const [sapFormData, setSapFormData] = useState<SAPNotificationFormPayload | null>(null);
  const [sapResponse, setSapResponse] = useState<SAPNotificationResponse | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  function openApproval(proposal: NotificationProposal) {
    setSelectedProposal(proposal);
    setModalMode("approve");
    setComments("");
    setActionError(null);
    setSapResponse(null);
  }

  function openRejection(proposal: NotificationProposal) {
    setSelectedProposal(proposal);
    setModalMode("reject");
    setReason("");
    setActionError(null);
    setSapResponse(null);
  }

  async function openSAPPreview(proposal: NotificationProposal) {
    setSelectedProposal(proposal);
    setModalMode("sap-preview");
    setActionError(null);
    setSapResponse(null);
    setActionLoading(true);
    try {
      setSapFormData(await proposals.getSAPFormData(proposal.proposal_id));
    } catch (error) {
      setActionError(toApiError(error).message);
    } finally {
      setActionLoading(false);
    }
  }

  async function confirmApproval() {
    if (!selectedProposal) return;
    setActionLoading(true);
    setActionError(null);
    try {
      const approved = await proposals.approve(selectedProposal.proposal_id, reviewerName, comments);
      setSelectedProposal(approved);
      setSapFormData(await proposals.getSAPFormData(approved.proposal_id));
      setModalMode("sap-preview");
    } catch (error) {
      setActionError(toApiError(error).message);
    } finally {
      setActionLoading(false);
    }
  }

  async function confirmRejection() {
    if (!selectedProposal) return;
    setActionLoading(true);
    setActionError(null);
    try {
      await proposals.reject(selectedProposal.proposal_id, reviewerName, reason);
      closeModal();
    } catch (error) {
      setActionError(toApiError(error).message);
    } finally {
      setActionLoading(false);
    }
  }

  async function createSAPNotification() {
    if (!selectedProposal || !sapFormData) return;
    setActionLoading(true);
    setActionError(null);
    try {
      const response = await proposals.createInSAP(selectedProposal.proposal_id, sapFormData);
      setSapResponse(response);
      setSelectedProposal((current) =>
        current
          ? {
              ...current,
              status: response.status,
              sap_notification_number: response.sap_notification_number,
            }
          : current,
      );
    } catch (error) {
      setActionError(toApiError(error).message);
    } finally {
      setActionLoading(false);
    }
  }

  function closeModal() {
    setSelectedProposal(null);
    setModalMode(null);
    setSapFormData(null);
    setSapResponse(null);
    setActionError(null);
  }

  if (proposals.loading) return <LoadingSkeleton rows={7} />;
  if (proposals.error) return <ErrorState message={proposals.error} onRetry={proposals.refresh} />;

  return (
    <div className="page-stack notifications-page">
      <PageHeader
        title="Notifications"
        description="Review AI-proposed maintenance notifications before creating SAP M1 notifications in IW21."
        actions={
          <button className="secondary-button" type="button" onClick={() => setShowHistory((value) => !value)}>
            <ClipboardCheck size={16} /> {showHistory ? "Show Pending" : "Show History"}
          </button>
        }
      />

      <section className="notification-summary-grid">
        <SummaryCard icon={BellRing} label="Pending proposals" value={proposals.pending.length} note="Awaiting manager approval" />
        <SummaryCard icon={ShieldCheck} label="Human approval" value="Required" note="No automatic SAP creation" />
        <SummaryCard icon={ClipboardCheck} label="SAP target" value="M1 / IW21" note="PM EES notification form" />
      </section>

      {!showHistory ? (
        <section className="notification-section">
          <div className="card-heading">
            <div>
              <h2>Pending Proposals</h2>
              <p>AI candidates generated from sensor thresholds, prediction risk, and component history.</p>
            </div>
          </div>

          {proposals.pending.length ? (
            <div className="proposal-grid">
              {proposals.pending.map((proposal) => (
                <ProposalCard
                  key={proposal.proposal_id}
                  proposal={proposal}
                  onApprove={() => openApproval(proposal)}
                  onReject={() => openRejection(proposal)}
                  onPreview={() => void openSAPPreview(proposal)}
                />
              ))}
            </div>
          ) : (
            <div className="state-box">
              <BellRing size={24} />
              <h3>No pending notification proposals</h3>
              <p>New proposals will appear here when asset sensor patterns exceed notification thresholds.</p>
            </div>
          )}
        </section>
      ) : (
        <HistorySection history={proposals.history} />
      )}

      {modalMode === "approve" && selectedProposal && (
        <ReviewModal title="Approve Notification Proposal" onClose={closeModal}>
          <ProposalMiniSummary proposal={selectedProposal} />
          <label className="form-field">
            Reviewer name
            <input value={reviewerName} onChange={(event) => setReviewerName(event.target.value)} />
          </label>
          <label className="form-field">
            Approval comments
            <textarea
              value={comments}
              onChange={(event) => setComments(event.target.value)}
              placeholder="Optional context for audit trail or SAP verifier..."
            />
          </label>
          {actionError && <p className="error-message">{actionError}</p>}
          <div className="modal-actions">
            <button className="secondary-button" type="button" onClick={closeModal}>
              Back
            </button>
            <button className="primary-button" type="button" onClick={() => void confirmApproval()} disabled={actionLoading || !reviewerName.trim()}>
              <CheckCircle2 size={16} /> Confirm Approval
            </button>
          </div>
        </ReviewModal>
      )}

      {modalMode === "reject" && selectedProposal && (
        <ReviewModal title="Reject Notification Proposal" onClose={closeModal}>
          <ProposalMiniSummary proposal={selectedProposal} />
          <label className="form-field">
            Reviewer name
            <input value={reviewerName} onChange={(event) => setReviewerName(event.target.value)} />
          </label>
          <label className="form-field">
            Rejection reason
            <textarea
              value={reason}
              onChange={(event) => setReason(event.target.value)}
              placeholder="Explain why this proposal should not become a SAP M1 notification..."
            />
          </label>
          {actionError && <p className="error-message">{actionError}</p>}
          <div className="modal-actions">
            <button className="secondary-button" type="button" onClick={closeModal}>
              Back
            </button>
            <button className="danger-button" type="button" onClick={() => void confirmRejection()} disabled={actionLoading || !reviewerName.trim() || !reason.trim()}>
              <XCircle size={16} /> Reject Proposal
            </button>
          </div>
        </ReviewModal>
      )}

      {modalMode === "sap-preview" && selectedProposal && (
        <ReviewModal title="SAP M1 Form Preview" onClose={closeModal} wide>
          {actionLoading && !sapFormData ? (
            <LoadingSkeleton rows={4} />
          ) : sapFormData ? (
            <>
              <SAPFormPreview formData={sapFormData} />
              <SAPInstructions />
              {sapResponse && (
                <div className="sap-success-box">
                  <CheckCircle2 size={18} />
                  <div>
                    <strong>SAP notification created</strong>
                    <p>{sapResponse.message}</p>
                    <span>Notification number: {sapResponse.sap_notification_number}</span>
                  </div>
                </div>
              )}
              {actionError && <p className="error-message">{actionError}</p>}
              <div className="modal-actions">
                <button className="secondary-button" type="button" onClick={closeModal}>
                  Back
                </button>
                {SAP_PORTAL_URL && (
                  <a className="secondary-button" href={SAP_PORTAL_URL} target="_blank" rel="noreferrer">
                    <ExternalLink size={16} /> Edit in SAP Easy Access
                  </a>
                )}
                <button
                  className="primary-button"
                  type="button"
                  onClick={() => void createSAPNotification()}
                  disabled={actionLoading || selectedProposal.status !== "APPROVED" || Boolean(sapResponse)}
                >
                  <ClipboardCheck size={16} /> Create in SAP
                </button>
              </div>
              {selectedProposal.status !== "APPROVED" && !sapResponse && (
                <p className="modal-hint">Approve this proposal first before SAP creation is enabled.</p>
              )}
            </>
          ) : (
            <ErrorState message={actionError || "SAP form preview is unavailable."} />
          )}
        </ReviewModal>
      )}
    </div>
  );
}

function ProposalCard({
  proposal,
  onApprove,
  onReject,
  onPreview,
}: {
  proposal: NotificationProposal;
  onApprove: () => void;
  onReject: () => void;
  onPreview: () => void;
}) {
  const thresholdLabel = `${formatNumber(proposal.current_value, 1)} vs ${formatNumber(proposal.threshold, 1)}`;
  return (
    <article className="proposal-card">
      <div className="proposal-card-top">
        <div>
          <span className="eyebrow">{proposal.asset_name}</span>
          <h3>{proposal.equipment_name}</h3>
        </div>
        <span className="badge badge-attention">{proposal.status}</span>
      </div>
      <div className="proposal-signal-grid">
        <Signal label="Sensor" value={titleCase(proposal.sensor_name)} />
        <Signal label="Current vs threshold" value={thresholdLabel} />
        <Signal label="AI confidence" value={formatPercent(proposal.ai_confidence, 0)} />
        <Signal label="Predicted failure" value={formatDateTime(proposal.predicted_failure_date)} />
      </div>
      <p>{proposal.failure_description}</p>
      <div className="proposal-actions">
        <button className="secondary-button" type="button" onClick={onPreview}>
          <Eye size={16} /> View SAP Form Preview
        </button>
        <button className="primary-button" type="button" onClick={onApprove}>
          <CheckCircle2 size={16} /> Approve
        </button>
        <button className="danger-button" type="button" onClick={onReject}>
          <XCircle size={16} /> Reject
        </button>
      </div>
    </article>
  );
}

function SummaryCard({ icon: Icon, label, value, note }: { icon: typeof BellRing; label: string; value: string | number; note: string }) {
  return (
    <div className="notification-summary-card">
      <Icon size={24} />
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <p>{note}</p>
      </div>
    </div>
  );
}

function Signal({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ReviewModal({
  title,
  children,
  onClose,
  wide = false,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
  wide?: boolean;
}) {
  return (
    <div className="modal-backdrop" role="presentation">
      <section className={wide ? "review-modal wide" : "review-modal"} role="dialog" aria-modal="true" aria-label={title}>
        <div className="review-modal-heading">
          <h2>{title}</h2>
          <button className="icon-button" type="button" onClick={onClose} aria-label="Close modal">
            <XCircle size={18} />
          </button>
        </div>
        {children}
      </section>
    </div>
  );
}

function ProposalMiniSummary({ proposal }: { proposal: NotificationProposal }) {
  return (
    <div className="proposal-mini-summary">
      <strong>{proposal.asset_name} / {proposal.equipment_name}</strong>
      <p>{proposal.failure_description}</p>
    </div>
  );
}

function SAPFormPreview({ formData }: { formData: SAPNotificationFormPayload }) {
  return (
    <div className="sap-form-preview">
      <FormRow label="Functional Location" value={formData.functional_location} />
      <FormRow label="Equipment" value={formData.equipment} />
      <FormRow label="Planner Group" value={formData.planner_group} />
      <FormRow label="Work Center" value={formData.work_center} />
      <FormRow label="Reported by" value={formData.reported_by} />
      <FormRow label="User Status" value={formData.user_status} />
      <FormRow label="Breakdown Duration" value={`${formatNumber(formData.breakdown_duration, 1)} minutes`} />
      <FormRow label="Unsafe Potential Risk" value={formData.unsafepotential_risk ? "Yes" : "No"} />
      <div className="sap-form-description">
        <span>Description</span>
        <p>{formData.description}</p>
      </div>
    </div>
  );
}

function FormRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function SAPInstructions() {
  return (
    <div className="sap-instructions">
      <h3>SAP Form Instructions</h3>
      <p>This notification will be created in SAP EES PM Module.</p>
      <ol>
        <li>Click "Create in SAP" to auto-create and receive a SAP notification number.</li>
        <li>Or manually create it in SAP Easy Access using the portal URL configured in your local environment.</li>
        <li>Sign in with your authorized SAP account. Open PM EES, then Create M1 notification.</li>
        <li>Fill the fields from the read-only preview above, then press Save.</li>
      </ol>
    </div>
  );
}

function HistorySection({ history }: { history: NotificationProposal[] }) {
  return (
    <section className="notification-section">
      <div className="card-heading">
        <div>
          <h2>Notification History</h2>
          <p>Approved, rejected, and SAP-created proposals with audit details.</p>
        </div>
      </div>
      {history.length ? (
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Asset</th>
                <th>Equipment</th>
                <th>Reviewer</th>
                <th>Review date</th>
                <th>SAP number</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.proposal_id}>
                  <td><span className="badge badge-unknown">{item.status}</span></td>
                  <td>{item.asset_name}</td>
                  <td>{item.equipment_name}</td>
                  <td>{item.reviewed_by || "Not available"}</td>
                  <td>{formatDateTime(item.review_date)}</td>
                  <td>{item.sap_notification_number || "Not created"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="muted">No notification history yet.</p>
      )}
    </section>
  );
}

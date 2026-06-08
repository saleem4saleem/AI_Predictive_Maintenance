import {
  BellRing,
  CheckCircle2,
  CircleAlert,
  ClipboardPlus,
  ExternalLink,
  Filter,
  Info,
  Plus,
  RefreshCw,
  Send,
  ShieldCheck,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { Card } from "../components/common/Card";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingSkeleton } from "../components/common/LoadingSkeleton";
import { PageHeader } from "../components/layout/PageHeader";
import { useAssetComponents } from "../hooks/useAssetComponents";
import { useMaintenanceNotifications } from "../hooks/useMaintenanceNotifications";
import type { AssetBasicResponse } from "../types/asset";
import type {
  MaintenanceNotificationCreateRequest,
  MaintenanceNotificationDraft,
  MaintenanceNotificationPriority,
  MaintenanceNotificationSource,
  MaintenanceNotificationStatus,
} from "../types/maintenanceNotification";
import { formatDateTime } from "../utils/date";
import { getProductionAssetDisplayName } from "../utils/assetImageMap";
import { titleCase } from "../utils/formatters";


interface MaintenanceNotificationsProps {
  assetId: number;
  assets: AssetBasicResponse[];
  onSelectAsset: (assetId: number) => void;
  initialDraft?: MaintenanceNotificationDraft | null;
  onDraftConsumed?: () => void;
}


interface NotificationFormState {
  asset_id: number;
  component_id: string;
  priority: MaintenanceNotificationPriority;
  short_text: string;
  description: string;
  failure_mode: string;
  suspected_cause: string;
  recommended_action: string;
  source: MaintenanceNotificationSource;
  requested_by: string;
}


export function MaintenanceNotifications({
  assetId,
  assets,
  onSelectAsset,
  initialDraft,
  onDraftConsumed,
}: MaintenanceNotificationsProps) {
  const [filterAssetId, setFilterAssetId] = useState<number | null>(null);
  const [showForm, setShowForm] = useState(Boolean(initialDraft));
  const [manualConfirmationId, setManualConfirmationId] = useState<string | null>(null);
  const [manualSAPNumber, setManualSAPNumber] = useState("");
  const [manualSAPNote, setManualSAPNote] = useState("");
  const [form, setForm] = useState<NotificationFormState>(() => createInitialForm(assetId));
  const components = useAssetComponents(form.asset_id);
  const notifications = useMaintenanceNotifications(filterAssetId);
  const selectedAsset = assets.find((asset) => asset.asset_id === form.asset_id);
  const selectedComponent = components.data?.components.find(
    (component) => component.component_id === Number(form.component_id),
  );

  useEffect(() => {
    if (!initialDraft) return;
    const nextAssetId = initialDraft.asset_id || assetId;
    setForm({
      asset_id: nextAssetId,
      component_id: initialDraft.component_id ? String(initialDraft.component_id) : "",
      priority: initialDraft.priority || "medium",
      short_text: initialDraft.short_text || "",
      description: initialDraft.description || "",
      failure_mode: initialDraft.failure_mode || "",
      suspected_cause: initialDraft.suspected_cause || "",
      recommended_action: initialDraft.recommended_action || "",
      source: initialDraft.source || "manual",
      requested_by: initialDraft.requested_by || "maintenance_manager",
    });
    setShowForm(true);
    onSelectAsset(nextAssetId);
    onDraftConsumed?.();
  }, [initialDraft, assetId, onDraftConsumed, onSelectAsset]);

  useEffect(() => {
    void notifications.refreshSAPStatus();
  }, [notifications.refreshSAPStatus]);

  function updateForm<Key extends keyof NotificationFormState>(
    key: Key,
    value: NotificationFormState[Key],
  ) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function handleAssetChange(nextAssetId: number) {
    onSelectAsset(nextAssetId);
    setForm((current) => ({
      ...current,
      asset_id: nextAssetId,
      component_id: "",
    }));
  }

  async function submitNotification(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedAsset) return;

    const payload: MaintenanceNotificationCreateRequest = {
      asset_id: selectedAsset.asset_id,
      asset_code: selectedAsset.asset_code,
      asset_name: selectedAsset.asset_name,
      component_id: selectedComponent?.component_id,
      component_code: selectedComponent?.component_code,
      component_name: selectedComponent?.component_name,
      notification_type: "M1",
      priority: form.priority,
      short_text: form.short_text.trim(),
      description: form.description.trim(),
      failure_mode: optionalText(form.failure_mode),
      suspected_cause: optionalText(form.suspected_cause),
      recommended_action: optionalText(form.recommended_action),
      source: form.source,
      requested_by: optionalText(form.requested_by),
    };

    await notifications.create(payload);
    setForm((current) => ({
      ...createInitialForm(current.asset_id),
      component_id: current.component_id,
      requested_by: current.requested_by,
    }));
  }

  async function confirmManualSAPNumber(notificationId: string) {
    if (!manualSAPNumber.trim()) return;
    await notifications.confirmSAPManually(
      notificationId,
      manualSAPNumber.trim(),
      manualSAPNote.trim() || undefined,
    );
    setManualConfirmationId(null);
    setManualSAPNumber("");
    setManualSAPNote("");
  }

  const filteredLabel = useMemo(() => {
    if (!filterAssetId) return "All assets";
    return getProductionAssetDisplayName(
      assets.find((asset) => asset.asset_id === filterAssetId),
    );
  }, [assets, filterAssetId]);

  return (
    <div className="page-stack maintenance-notifications-page">
      <PageHeader
        title="Maintenance Notifications"
        description="Create and track local test maintenance notifications using a SAP PM-ready structure."
        actions={
          <button className="primary-button" type="button" onClick={() => setShowForm((value) => !value)}>
            <Plus size={16} /> {showForm ? "Close Form" : "Create Notification"}
          </button>
        }
      />

      <SAPStatusPanel
        status={notifications.sapStatus}
        loading={notifications.sapLoading}
        onRefresh={() => void notifications.refreshSAPStatus()}
      />

      <div className="sap-disabled-banner">
        <Info size={22} />
        <div>
          <strong>Authorized SAP access only</strong>
          <p>
            SAP integration may only work from an authorized company device/network/VPN/Zscaler session. This app
            will not bypass company security. Local notifications are test records until SAP confirms a notification
            number.
          </p>
        </div>
      </div>

      {notifications.success && (
        <div className="notification-created-banner">
          <ClipboardPlus size={22} />
          <div>
            <strong>{notifications.success.notification_id}</strong>
            <p>{notifications.success.message}</p>
          </div>
        </div>
      )}

      {showForm && (
        <Card
          title="Create Local Test Notification"
          subtitle="All fields remain inside the application until a real SAP integration is configured."
        >
          <form className="maintenance-notification-form" onSubmit={(event) => void submitNotification(event)}>
            <div className="notification-form-grid">
              <FormField label="Asset">
                <select value={form.asset_id} onChange={(event) => handleAssetChange(Number(event.target.value))}>
                  {assets.map((asset) => (
                    <option key={asset.asset_id} value={asset.asset_id}>
                      {getProductionAssetDisplayName(asset)} ({asset.asset_code})
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Component / Part">
                <select
                  value={form.component_id}
                  onChange={(event) => updateForm("component_id", event.target.value)}
                  disabled={components.loading}
                >
                  <option value="">Asset level notification</option>
                  {(components.data?.components || []).map((component) => (
                    <option key={component.component_id} value={component.component_id}>
                      {component.component_name} ({component.component_code})
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Priority">
                <select
                  value={form.priority}
                  onChange={(event) => updateForm("priority", event.target.value as MaintenanceNotificationPriority)}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </FormField>

              <FormField label="Source">
                <select
                  value={form.source}
                  onChange={(event) => updateForm("source", event.target.value as MaintenanceNotificationSource)}
                >
                  <option value="manual">Manual</option>
                  <option value="ai_recommendation">AI recommendation</option>
                  <option value="condition_monitoring">Condition monitoring</option>
                  <option value="predictive_maintenance">Predictive maintenance</option>
                  <option value="component_history">Component history</option>
                </select>
              </FormField>
            </div>

            {components.error && (
              <p className="form-note">Component list is unavailable. You can still create an asset-level notification.</p>
            )}

            <FormField label="Short text">
              <input
                required
                maxLength={255}
                value={form.short_text}
                onChange={(event) => updateForm("short_text", event.target.value)}
                placeholder="Short SAP-ready problem summary"
              />
            </FormField>

            <FormField label="Description">
              <textarea
                required
                value={form.description}
                onChange={(event) => updateForm("description", event.target.value)}
                placeholder="Describe the observed problem, evidence, and operational impact."
              />
            </FormField>

            <div className="notification-form-grid">
              <FormField label="Failure mode">
                <input
                  value={form.failure_mode}
                  onChange={(event) => updateForm("failure_mode", event.target.value)}
                  placeholder="Example: vacuum loss"
                />
              </FormField>
              <FormField label="Suspected cause">
                <input
                  value={form.suspected_cause}
                  onChange={(event) => updateForm("suspected_cause", event.target.value)}
                  placeholder="Example: suction cup wear"
                />
              </FormField>
            </div>

            <FormField label="Recommended action">
              <textarea
                value={form.recommended_action}
                onChange={(event) => updateForm("recommended_action", event.target.value)}
                placeholder="Recommended inspection, repair, or replacement action."
              />
            </FormField>

            <FormField label="Requested by">
              <input
                value={form.requested_by}
                onChange={(event) => updateForm("requested_by", event.target.value)}
                placeholder="Maintenance manager"
              />
            </FormField>

            {notifications.error && <p className="error-message">{notifications.error}</p>}
            <div className="notification-form-actions">
              <button className="secondary-button" type="button" onClick={() => setShowForm(false)}>
                Cancel
              </button>
              <button
                className="primary-button"
                type="submit"
                disabled={notifications.submitting || !form.short_text.trim() || !form.description.trim()}
              >
                <ClipboardPlus size={16} />
                {notifications.submitting ? "Creating..." : "Create Local Notification"}
              </button>
            </div>
          </form>
        </Card>
      )}

      <Card
        title="Maintenance Notifications"
        subtitle={`${notifications.total} local or SAP-ready records shown for ${filteredLabel}.`}
        action={
          <div className="notification-list-actions">
            <label className="notification-filter">
              <Filter size={15} />
              <select
                value={filterAssetId ?? ""}
                onChange={(event) => setFilterAssetId(event.target.value ? Number(event.target.value) : null)}
              >
                <option value="">All assets</option>
                {assets.map((asset) => (
                  <option key={asset.asset_id} value={asset.asset_id}>
                    {getProductionAssetDisplayName(asset)}
                  </option>
                ))}
              </select>
            </label>
            <button className="icon-button" type="button" onClick={() => void notifications.refresh()} title="Refresh notifications">
              <RefreshCw size={16} />
            </button>
          </div>
        }
      >
        {notifications.loading ? (
          <LoadingSkeleton rows={4} />
        ) : notifications.error && notifications.notifications.length === 0 ? (
          <ErrorState message={notifications.error} onRetry={notifications.refresh} />
        ) : notifications.notifications.length ? (
          <div className="maintenance-notification-list">
            {notifications.notifications.map((notification) => (
              <article className="maintenance-notification-row" key={notification.notification_id}>
                <div className="notification-id-cell">
                  <BellRing size={18} />
                  <div>
                    <strong>{notification.notification_id}</strong>
                    <span>{formatDateTime(notification.created_at)}</span>
                  </div>
                </div>
                <div>
                  <span>Asset / Component</span>
                  <strong>{notification.asset_name || notification.asset_code}</strong>
                  <small>{notification.component_name || "Asset level"}</small>
                </div>
                <div>
                  <span>Problem</span>
                  <strong>{notification.short_text}</strong>
                  <small>{titleCase(notification.source)}</small>
                </div>
                <div>
                  <span>Priority</span>
                  <PriorityBadge priority={notification.priority} />
                </div>
                <div>
                  <span>Status</span>
                  <NotificationStatusBadge status={notification.status} />
                  <small>{notification.sap_notification_number || "No SAP number"}</small>
                </div>
                <div className="notification-row-actions">
                  <span>SAP Actions</span>
                  <div>
                    {notification.status === "local_test" && (
                      <button
                        className="secondary-button"
                        type="button"
                        disabled={notifications.actionNotificationId === notification.notification_id}
                        onClick={() => void notifications.markReadyForSAP(notification.notification_id)}
                      >
                        <ShieldCheck size={15} /> Mark Ready
                      </button>
                    )}
                    {notification.status !== "sent_to_sap" && (
                      <button
                        className="secondary-button"
                        type="button"
                        disabled={notifications.actionNotificationId === notification.notification_id}
                        onClick={() => void notifications.sendToSAP(notification.notification_id)}
                      >
                        <Send size={15} /> Start SAP Test
                      </button>
                    )}
                    {notification.status !== "sent_to_sap" && (
                      <button
                        className="secondary-button"
                        type="button"
                        onClick={() => {
                          setManualConfirmationId(
                            manualConfirmationId === notification.notification_id
                              ? null
                              : notification.notification_id,
                          );
                          setManualSAPNumber("");
                          setManualSAPNote("");
                        }}
                      >
                        <CheckCircle2 size={15} /> Enter SAP Number
                      </button>
                    )}
                  </div>
                </div>
                <p className="notification-status-message">{notification.message}</p>
                {manualConfirmationId === notification.notification_id && (
                  <div className="manual-sap-confirmation">
                    <label>
                      SAP notification number
                      <input
                        value={manualSAPNumber}
                        onChange={(event) => setManualSAPNumber(event.target.value)}
                        placeholder="Enter the number confirmed by SAP"
                      />
                    </label>
                    <label>
                      Confirmation note
                      <input
                        value={manualSAPNote}
                        onChange={(event) => setManualSAPNote(event.target.value)}
                        placeholder="Optional note about manual IW21 creation"
                      />
                    </label>
                    <button
                      className="primary-button"
                      type="button"
                      disabled={!manualSAPNumber.trim() || notifications.actionNotificationId === notification.notification_id}
                      onClick={() => void confirmManualSAPNumber(notification.notification_id)}
                    >
                      Confirm SAP Number
                    </button>
                  </div>
                )}
              </article>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No maintenance notifications found"
            message="Create a local test notification or change the asset filter."
          />
        )}
      </Card>

      <div className="notification-safety-note">
        <CircleAlert size={18} />
        <p>
          A `local_test` notification confirms the application workflow only. It is not proof that SAP PM, IW21,
          or SAP Easy Access received a notification.
        </p>
      </div>
    </div>
  );
}


function FormField({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="maintenance-notification-field">
      <span>{label}</span>
      {children}
    </label>
  );
}


function PriorityBadge({ priority }: { priority: string }) {
  return <span className={`notification-priority priority-${priority}`}>{titleCase(priority)}</span>;
}


function NotificationStatusBadge({ status }: { status: MaintenanceNotificationStatus }) {
  return <span className={`notification-status status-${status}`}>{titleCase(status)}</span>;
}


function SAPStatusPanel({
  status,
  loading,
  onRefresh,
}: {
  status: ReturnType<typeof useMaintenanceNotifications>["sapStatus"];
  loading: boolean;
  onRefresh: () => void;
}) {
  const portalReachable = Boolean(status?.reachable);
  return (
    <Card
      title="SAP Integration Status"
      subtitle="Connectivity is checked by the backend without exposing SAP credentials to the browser."
      action={
        <button className="secondary-button" type="button" onClick={onRefresh} disabled={loading}>
          <RefreshCw size={16} /> {loading ? "Checking..." : "Check SAP Status"}
        </button>
      }
    >
      <div className="sap-status-layout">
        <div className="sap-status-facts">
          <div>
            <span>Integration</span>
            <strong>{status?.enabled ? "Enabled" : "Disabled"}</strong>
          </div>
          <div>
            <span>Configuration</span>
            <strong>{status?.configured ? "Configured" : "Not configured"}</strong>
          </div>
          <div>
            <span>Portal</span>
            <strong>{portalReachable ? "Reachable" : "Not confirmed"}</strong>
          </div>
          <div>
            <span>Mode</span>
            <strong>{status?.status ? titleCase(status.status) : "Local test"}</strong>
          </div>
        </div>
        <div className={`sap-status-message ${portalReachable ? "reachable" : ""}`}>
          <ShieldCheck size={20} />
          <p>{status?.message || "SAP integration status has not been checked yet."}</p>
        </div>
        {status?.portal_url && (
          <a className="secondary-button sap-portal-link" href={status.portal_url} target="_blank" rel="noreferrer">
            <ExternalLink size={16} /> Open SAP Portal
          </a>
        )}
      </div>
    </Card>
  );
}


function createInitialForm(assetId: number): NotificationFormState {
  return {
    asset_id: assetId,
    component_id: "",
    priority: "medium",
    short_text: "",
    description: "",
    failure_mode: "",
    suspected_cause: "",
    recommended_action: "",
    source: "manual",
    requested_by: "maintenance_manager",
  };
}


function optionalText(value: string): string | null {
  const normalized = value.trim();
  return normalized || null;
}

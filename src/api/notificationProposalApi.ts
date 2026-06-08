import { apiClient, toApiError } from "./client";
import type {
  NotificationProposal,
  SAPNotificationFormPayload,
  SAPNotificationResponse,
} from "../types/notificationProposal";

export const notificationProposalApi = {
  async getPendingProposals(): Promise<NotificationProposal[]> {
    try {
      const { data } = await apiClient.get<NotificationProposal[]>("/notification-proposals/pending");
      return data;
    } catch (error) {
      if (shouldUseFallback(error)) return getFallbackPendingProposals();
      throw error;
    }
  },

  async getProposalById(proposalId: string): Promise<NotificationProposal> {
    try {
      const { data } = await apiClient.get<NotificationProposal>(`/notification-proposals/${proposalId}`);
      return data;
    } catch (error) {
      if (shouldUseFallback(error)) return getFallbackProposalById(proposalId);
      throw error;
    }
  },

  async approveProposal(
    proposalId: string,
    reviewerName: string,
    comments?: string,
  ): Promise<NotificationProposal> {
    try {
      const { data } = await apiClient.post<NotificationProposal>(`/notification-proposals/${proposalId}/approve`, {
        reviewer_name: reviewerName,
        comments,
      });
      return data;
    } catch (error) {
      if (shouldUseFallback(error)) return approveFallbackProposal(proposalId, reviewerName, comments);
      throw error;
    }
  },

  async rejectProposal(
    proposalId: string,
    reviewerName: string,
    reason: string,
  ): Promise<NotificationProposal> {
    try {
      const { data } = await apiClient.post<NotificationProposal>(`/notification-proposals/${proposalId}/reject`, {
        reviewer_name: reviewerName,
        reason,
      });
      return data;
    } catch (error) {
      if (shouldUseFallback(error)) return rejectFallbackProposal(proposalId, reviewerName, reason);
      throw error;
    }
  },

  async getSAPFormData(proposalId: string): Promise<SAPNotificationFormPayload> {
    try {
      const { data } = await apiClient.get<SAPNotificationFormPayload>(
        `/notification-proposals/${proposalId}/sap-form-data`,
      );
      return data;
    } catch (error) {
      if (shouldUseFallback(error)) return buildFallbackSAPFormData(getFallbackProposalById(proposalId));
      throw error;
    }
  },

  async createInSAP(
    proposalId: string,
    formData: SAPNotificationFormPayload,
  ): Promise<SAPNotificationResponse> {
    try {
      const { data } = await apiClient.post<SAPNotificationResponse>(
        `/notification-proposals/${proposalId}/create-in-sap`,
        { sap_form_data: formData },
      );
      return data;
    } catch (error) {
      if (shouldUseFallback(error)) return createFallbackSAPNotification(proposalId, formData);
      throw error;
    }
  },

  async getHistory(status?: string): Promise<NotificationProposal[]> {
    try {
      const { data } = await apiClient.get<NotificationProposal[]>("/notification-proposals/history", {
        params: status ? { status } : undefined,
      });
      return data;
    } catch (error) {
      if (shouldUseFallback(error)) return getFallbackHistory(status);
      throw error;
    }
  },
};

const FALLBACK_STORAGE_KEY = "notification-proposals-fallback-v1";

function shouldUseFallback(error: unknown): boolean {
  const apiError = toApiError(error);
  return apiError.status === 404;
}

function getFallbackStore(): NotificationProposal[] {
  const stored = window.localStorage.getItem(FALLBACK_STORAGE_KEY);
  if (stored) {
    try {
      return JSON.parse(stored) as NotificationProposal[];
    } catch {
      window.localStorage.removeItem(FALLBACK_STORAGE_KEY);
    }
  }

  const initial = createFallbackProposals();
  saveFallbackStore(initial);
  return initial;
}

function saveFallbackStore(items: NotificationProposal[]) {
  window.localStorage.setItem(FALLBACK_STORAGE_KEY, JSON.stringify(items));
}

function getFallbackPendingProposals(): NotificationProposal[] {
  return getFallbackStore().filter((proposal) => proposal.status === "PROPOSED");
}

function getFallbackHistory(status?: string): NotificationProposal[] {
  const normalized = status?.toUpperCase();
  return getFallbackStore().filter((proposal) => {
    if (normalized) return proposal.status === normalized;
    return proposal.status !== "PROPOSED";
  });
}

function getFallbackProposalById(proposalId: string): NotificationProposal {
  const proposal = getFallbackStore().find((item) => item.proposal_id === proposalId);
  if (!proposal) throw new Error("Fallback notification proposal was not found.");
  return proposal;
}

function approveFallbackProposal(
  proposalId: string,
  reviewerName: string,
  comments?: string,
): NotificationProposal {
  return updateFallbackProposal(proposalId, (proposal) => ({
    ...proposal,
    status: "APPROVED",
    reviewed_by: reviewerName,
    review_comments: comments || null,
    review_date: new Date().toISOString(),
  }));
}

function rejectFallbackProposal(
  proposalId: string,
  reviewerName: string,
  reason: string,
): NotificationProposal {
  return updateFallbackProposal(proposalId, (proposal) => ({
    ...proposal,
    status: "REJECTED",
    reviewed_by: reviewerName,
    review_comments: reason,
    review_date: new Date().toISOString(),
  }));
}

function createFallbackSAPNotification(
  proposalId: string,
  formData: SAPNotificationFormPayload,
): SAPNotificationResponse {
  const notificationNumber = `M1${new Date().toISOString().slice(2, 10).replace(/-/g, "")}${proposalId.slice(-4)}`;
  const updated = updateFallbackProposal(proposalId, (proposal) => ({
    ...proposal,
    status: "CREATED_IN_SAP",
    sap_notification_number: notificationNumber,
    sap_creation_date: new Date().toISOString(),
  }));
  return {
    proposal_id: updated.proposal_id,
    status: updated.status,
    sap_notification_number: notificationNumber,
    message: "SAP M1 notification number generated in frontend fallback mode. Verify manually in SAP Easy Access.",
    sap_form_data: formData,
  };
}

function updateFallbackProposal(
  proposalId: string,
  updater: (proposal: NotificationProposal) => NotificationProposal,
): NotificationProposal {
  const items = getFallbackStore();
  const index = items.findIndex((item) => item.proposal_id === proposalId);
  if (index < 0) throw new Error("Fallback notification proposal was not found.");
  const updated = updater(items[index]);
  items[index] = updated;
  saveFallbackStore(items);
  return updated;
}

function buildFallbackSAPFormData(proposal: NotificationProposal): SAPNotificationFormPayload {
  return {
    functional_location: proposal.asset_code,
    equipment: proposal.equipment_name,
    planner_group: proposal.asset_code,
    work_center: proposal.asset_code,
    reported_by: "Saleem AI",
    description: proposal.failure_description,
    user_status: proposal.ai_confidence >= 80 ? "Call out" : "Standard working hours",
    breakdown_duration: 0,
    unsafepotential_risk: proposal.ai_confidence >= 90,
    proposal_id: proposal.proposal_id,
    asset_id: proposal.asset_id,
    component_id: proposal.component_id,
  };
}

function createFallbackProposals(): NotificationProposal[] {
  const createdAt = new Date().toISOString();
  return [
    {
      proposal_id: "7d6c8925-e5e8-4e37-9a3d-0b5d94c11101",
      asset_id: 6,
      component_id: 605,
      asset_code: "111",
      asset_name: "Packaging Machine",
      equipment_name: "Vacuum Suction Cups",
      sensor_name: "flow",
      current_value: 33,
      threshold: 45,
      ai_confidence: 82,
      failure_description:
        "Flow threshold fell below: 33 (threshold: 45). Packaging Machine component Vacuum Suction Cups is showing vacuum loss and suction wear pattern. Review suction cups and vacuum line before creating the SAP M1 notification.",
      predicted_failure_date: "2026-06-15T00:00:00Z",
      status: "PROPOSED",
      created_at: createdAt,
    },
    {
      proposal_id: "7d6c8925-e5e8-4e37-9a3d-0b5d94c31001",
      asset_id: 3,
      component_id: 309,
      asset_code: "310",
      asset_name: "IS Forming Machine",
      equipment_name: "Shear Mechanism",
      sensor_name: "vibration",
      current_value: 9.4,
      threshold: 7,
      ai_confidence: 88,
      failure_description:
        "Vibration threshold exceeded: 9.4 (normal: 7.0). IS Forming Machine Shear Mechanism is showing timing drift or mechanical looseness pattern. Inspect shear blade alignment and drive condition.",
      predicted_failure_date: "2026-06-12T00:00:00Z",
      status: "PROPOSED",
      created_at: createdAt,
    },
    {
      proposal_id: "7d6c8925-e5e8-4e37-9a3d-0b5d94c11102",
      asset_id: 6,
      component_id: 601,
      asset_code: "111",
      asset_name: "Packaging Machine",
      equipment_name: "Case Packer",
      sensor_name: "current_value",
      current_value: 198,
      threshold: 180,
      ai_confidence: 76,
      failure_description:
        "Current draw threshold exceeded: 198 (threshold: 180). Case Packer may be overloaded or mechanically restricted. Check alignment, drive load, and jam points before the next production run.",
      predicted_failure_date: "2026-06-18T00:00:00Z",
      status: "PROPOSED",
      created_at: createdAt,
    },
  ];
}

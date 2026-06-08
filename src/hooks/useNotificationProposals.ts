import { useCallback, useEffect, useState } from "react";
import { notificationProposalApi } from "../api/notificationProposalApi";
import { toApiError } from "../api/client";
import type {
  NotificationProposal,
  SAPNotificationFormPayload,
  SAPNotificationResponse,
} from "../types/notificationProposal";

export function useNotificationProposals() {
  const [pending, setPending] = useState<NotificationProposal[]>([]);
  const [history, setHistory] = useState<NotificationProposal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [pendingData, historyData] = await Promise.all([
        notificationProposalApi.getPendingProposals(),
        notificationProposalApi.getHistory(),
      ]);
      setPending(pendingData);
      setHistory(historyData);
    } catch (err) {
      setError(toApiError(err).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function approve(proposalId: string, reviewerName: string, comments?: string) {
    const proposal = await notificationProposalApi.approveProposal(proposalId, reviewerName, comments);
    await refresh();
    return proposal;
  }

  async function reject(proposalId: string, reviewerName: string, reason: string) {
    const proposal = await notificationProposalApi.rejectProposal(proposalId, reviewerName, reason);
    await refresh();
    return proposal;
  }

  async function getSAPFormData(proposalId: string): Promise<SAPNotificationFormPayload> {
    return notificationProposalApi.getSAPFormData(proposalId);
  }

  async function createInSAP(
    proposalId: string,
    formData: SAPNotificationFormPayload,
  ): Promise<SAPNotificationResponse> {
    const response = await notificationProposalApi.createInSAP(proposalId, formData);
    await refresh();
    return response;
  }

  return {
    pending,
    history,
    loading,
    error,
    refresh,
    approve,
    reject,
    getSAPFormData,
    createInSAP,
  };
}

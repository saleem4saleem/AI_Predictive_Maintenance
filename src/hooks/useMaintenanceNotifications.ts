import { useCallback, useEffect, useState } from "react";
import {
  confirmSAPNotificationManually,
  createMaintenanceNotification,
  getSAPIntegrationStatus,
  getMaintenanceNotifications,
  markMaintenanceNotificationReadyForSAP,
  sendMaintenanceNotificationToSAP,
} from "../api/maintenanceNotificationApi";
import { toApiError } from "../api/client";
import type {
  MaintenanceNotification,
  MaintenanceNotificationCreateRequest,
  SAPIntegrationStatus,
} from "../types/maintenanceNotification";


export function useMaintenanceNotifications(assetId?: number | null) {
  const [notifications, setNotifications] = useState<MaintenanceNotification[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<MaintenanceNotification | null>(null);
  const [sapStatus, setSapStatus] = useState<SAPIntegrationStatus | null>(null);
  const [sapLoading, setSapLoading] = useState(false);
  const [actionNotificationId, setActionNotificationId] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getMaintenanceNotifications(assetId);
      setNotifications(response.notifications);
    } catch (requestError) {
      setError(toApiError(requestError).message);
    } finally {
      setLoading(false);
    }
  }, [assetId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const create = useCallback(
    async (payload: MaintenanceNotificationCreateRequest) => {
      setSubmitting(true);
      setError(null);
      setSuccess(null);
      try {
        const notification = await createMaintenanceNotification(payload);
        setSuccess(notification);
        await refresh();
        return notification;
      } catch (requestError) {
        const message = toApiError(requestError).message;
        setError(message);
        throw requestError;
      } finally {
        setSubmitting(false);
      }
    },
    [refresh],
  );

  const refreshSAPStatus = useCallback(async () => {
    setSapLoading(true);
    setError(null);
    try {
      const status = await getSAPIntegrationStatus();
      setSapStatus(status);
      return status;
    } catch (requestError) {
      setError(toApiError(requestError).message);
      throw requestError;
    } finally {
      setSapLoading(false);
    }
  }, []);

  const runNotificationAction = useCallback(
    async (
      notificationId: string,
      action: () => Promise<MaintenanceNotification>,
    ) => {
      setActionNotificationId(notificationId);
      setError(null);
      setSuccess(null);
      try {
        const notification = await action();
        setSuccess(notification);
        await refresh();
        return notification;
      } catch (requestError) {
        setError(toApiError(requestError).message);
        throw requestError;
      } finally {
        setActionNotificationId(null);
      }
    },
    [refresh],
  );

  const markReadyForSAP = useCallback(
    (notificationId: string) =>
      runNotificationAction(
        notificationId,
        () => markMaintenanceNotificationReadyForSAP(notificationId),
      ),
    [runNotificationAction],
  );

  const sendToSAP = useCallback(
    (notificationId: string) =>
      runNotificationAction(
        notificationId,
        () => sendMaintenanceNotificationToSAP(notificationId),
      ),
    [runNotificationAction],
  );

  const confirmSAPManually = useCallback(
    (notificationId: string, sapNotificationNumber: string, note?: string) =>
      runNotificationAction(
        notificationId,
        () =>
          confirmSAPNotificationManually(notificationId, {
            sap_notification_number: sapNotificationNumber,
            note,
          }),
      ),
    [runNotificationAction],
  );

  return {
    notifications,
    total: notifications.length,
    loading,
    submitting,
    error,
    success,
    sapStatus,
    sapLoading,
    actionNotificationId,
    refresh,
    create,
    refreshSAPStatus,
    markReadyForSAP,
    sendToSAP,
    confirmSAPManually,
    clearSuccess: () => setSuccess(null),
  };
}

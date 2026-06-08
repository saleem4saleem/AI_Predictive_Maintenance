import { apiClient } from "./client";
import type {
  MaintenanceNotification,
  MaintenanceNotificationCreateRequest,
  MaintenanceNotificationListResponse,
  SAPIntegrationStatus,
  SAPManualConfirmationRequest,
} from "../types/maintenanceNotification";


export async function createMaintenanceNotification(
  payload: MaintenanceNotificationCreateRequest,
): Promise<MaintenanceNotification> {
  const { data } = await apiClient.post<MaintenanceNotification>(
    "/maintenance-notifications",
    payload,
  );
  return data;
}


export async function getMaintenanceNotifications(
  assetId?: number | null,
): Promise<MaintenanceNotificationListResponse> {
  const { data } = await apiClient.get<MaintenanceNotificationListResponse>(
    "/maintenance-notifications",
    { params: assetId ? { asset_id: assetId } : undefined },
  );
  return data;
}


export async function getMaintenanceNotification(
  notificationId: string,
): Promise<MaintenanceNotification> {
  const { data } = await apiClient.get<MaintenanceNotification>(
    `/maintenance-notifications/${notificationId}`,
  );
  return data;
}


export async function getSAPIntegrationStatus(): Promise<SAPIntegrationStatus> {
  const { data } = await apiClient.get<SAPIntegrationStatus>(
    "/maintenance-notifications/sap/status",
  );
  return data;
}


export async function markMaintenanceNotificationReadyForSAP(
  notificationId: string,
): Promise<MaintenanceNotification> {
  const { data } = await apiClient.post<MaintenanceNotification>(
    `/maintenance-notifications/${notificationId}/mark-ready-for-sap`,
  );
  return data;
}


export async function sendMaintenanceNotificationToSAP(
  notificationId: string,
): Promise<MaintenanceNotification> {
  const { data } = await apiClient.post<MaintenanceNotification>(
    `/maintenance-notifications/${notificationId}/send-to-sap`,
  );
  return data;
}


export async function confirmSAPNotificationManually(
  notificationId: string,
  payload: SAPManualConfirmationRequest,
): Promise<MaintenanceNotification> {
  const { data } = await apiClient.post<MaintenanceNotification>(
    `/maintenance-notifications/${notificationId}/sap-confirm`,
    payload,
  );
  return data;
}

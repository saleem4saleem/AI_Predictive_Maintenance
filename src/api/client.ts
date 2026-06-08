import axios, { AxiosError } from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export interface ApiClientError {
  message: string;
  status?: number;
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

export function toApiError(error: unknown): ApiClientError {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ error?: { message?: string }; detail?: string }>;
    const status = axiosError.response?.status;
    const message =
      axiosError.response?.data?.error?.message ||
      axiosError.response?.data?.detail ||
      axiosError.message ||
      "Backend is not reachable. Please check the API server.";
    return { message, status };
  }

  if (error instanceof Error) {
    return { message: error.message };
  }

  return { message: "Backend is not reachable. Please check the API server." };
}

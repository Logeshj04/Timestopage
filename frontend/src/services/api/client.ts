import axios, { AxiosError } from "axios";

const TOKEN_KEY = "pdms_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"}/api`,
  timeout: 60000,
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function apiErrorMessage(error: unknown, fallback = "Unable to complete the request. Please try again."): string {
  const axiosError = error as AxiosError<{ error?: { message?: string } }>;
  return axiosError.response?.data?.error?.message || fallback;
}

export async function downloadBlob(url: string, params: object, filename: string): Promise<void> {
  const response = await api.get(url, { params, responseType: "blob" });
  const contentType = String(response.headers["content-type"] ?? "");
  if (contentType.includes("application/json")) {
    const text = await (response.data as Blob).text();
    const parsed = JSON.parse(text) as { error?: { message?: string } };
    throw new Error(parsed.error?.message ?? "Unable to generate the report.");
  }
  const blob = new Blob([response.data]);
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(objectUrl);
}

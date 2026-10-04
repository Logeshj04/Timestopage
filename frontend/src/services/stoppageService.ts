import type { Paginated, ReportFilters, StoppageRecord } from "../types";
import { api } from "./api/client";

export interface StoppagePayload {
  production_date: string;
  shift_id: string;
  supervisor_id: string;
  machine_id: string;
  stoppage_reason_id: string;
  duration_minutes: number;
  details?: string | null;
  remarks?: string | null;
}

export const stoppageService = {
  list: (params: ReportFilters & { page?: number; page_size?: number; sort_by?: string; sort_order?: string }) =>
    api.get<Paginated<StoppageRecord>>("/stoppages", { params }).then((r) => r.data),
  get: (id: string) => api.get<StoppageRecord>(`/stoppages/${id}`).then((r) => r.data),
  create: (body: StoppagePayload) => api.post<StoppageRecord>("/stoppages", body).then((r) => r.data),
  update: (id: string, body: Partial<StoppagePayload>) => api.patch<StoppageRecord>(`/stoppages/${id}`, body).then((r) => r.data),
  remove: (id: string) => api.delete(`/stoppages/${id}`),
};

import type { DashboardSummary, ReportFilters } from "../types";
import { api, downloadBlob } from "./api/client";

export const dashboardService = {
  summary: (params: ReportFilters) => api.get<DashboardSummary>("/dashboard/summary", { params }).then((r) => r.data),
};

export const reportService = {
  excel: (params: ReportFilters & { report_type: string }, filename: string) =>
    downloadBlob("/reports/excel", params, filename),
  pdf: (params: ReportFilters, filename: string) => downloadBlob("/reports/pdf", params, filename),
};

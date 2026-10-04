export type UserRole = "admin" | "supervisor";

export interface User {
  id: string;
  username: string;
  role: UserRole;
  supervisor_id: string | null;
  is_active: boolean;
}

export interface Supervisor {
  id: string;
  name: string;
  active: boolean;
}

export interface Machine {
  id: string;
  code: string;
  name: string | null;
  active: boolean;
}

export interface Shift {
  id: string;
  code: string;
  name: string;
  start_time: string;
  end_time: string;
  crosses_midnight: boolean;
  sort_order: number;
  active: boolean;
}

export interface StoppageReason {
  id: string;
  name: string;
  requires_details: boolean;
  details_label: string | null;
  measurement_type: string;
  sort_order: number;
  notes: string | null;
  active: boolean;
}

export interface StoppageRecord {
  id: string;
  production_date: string;
  shift_id: string;
  supervisor_id: string;
  machine_id: string;
  stoppage_reason_id: string;
  duration_minutes: number;
  details: string | null;
  remarks: string | null;
  created_at: string;
  updated_at: string;
  created_by: string | null;
  updated_by: string | null;
  shift: Shift;
  supervisor: Supervisor;
  machine: Machine;
  reason: StoppageReason;
}

export interface Pagination {
  page: number;
  page_size: number;
  total: number;
}

export interface Paginated<T> {
  data: T[];
  pagination: Pagination;
}

export interface ReportFilters {
  date_from?: string;
  date_to?: string;
  shift_id?: string;
  supervisor_id?: string;
  machine_id?: string;
  reason_id?: string;
  search?: string;
}

export interface NamedTotal {
  id: string;
  name: string;
  downtime_minutes: number;
  stoppage_count: number;
  average_minutes: number;
}

export interface TrendPoint {
  period: string;
  downtime_minutes: number;
  stoppage_count: number;
}

export interface DashboardSummary {
  kpis: {
    total_downtime_minutes: number;
    current_shift_downtime_minutes: number;
    today_downtime_minutes: number;
    total_entries: number;
    current_production_date: string;
    current_shift_code: string;
  };
  machines: NamedTotal[];
  reasons: NamedTotal[];
  shifts: NamedTotal[];
  daily_trend: TrendPoint[];
  weekly_trend: TrendPoint[];
  monthly_trend: TrendPoint[];
  recent: StoppageRecord[];
}

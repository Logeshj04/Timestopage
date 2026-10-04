import type { Machine, Shift, StoppageReason, Supervisor, User } from "../types";
import { api } from "./api/client";

export const masterDataService = {
  supervisors: (activeOnly = false) =>
    api.get<Supervisor[]>("/supervisors", { params: { active_only: activeOnly } }).then((r) => r.data),
  machines: (activeOnly = false) =>
    api.get<Machine[]>("/machines", { params: { active_only: activeOnly } }).then((r) => r.data),
  shifts: (activeOnly = false) =>
    api.get<Shift[]>("/shifts", { params: { active_only: activeOnly } }).then((r) => r.data),
  reasons: (activeOnly = false) =>
    api.get<StoppageReason[]>("/stoppage-reasons", { params: { active_only: activeOnly } }).then((r) => r.data),
  users: () => api.get<User[]>("/users").then((r) => r.data),
  createSupervisor: (body: Partial<Supervisor>) => api.post("/supervisors", body).then((r) => r.data),
  updateSupervisor: (id: string, body: Partial<Supervisor>) => api.patch(`/supervisors/${id}`, body).then((r) => r.data),
  createMachine: (body: Partial<Machine>) => api.post("/machines", body).then((r) => r.data),
  updateMachine: (id: string, body: Partial<Machine>) => api.patch(`/machines/${id}`, body).then((r) => r.data),
  createShift: (body: Partial<Shift>) => api.post("/shifts", body).then((r) => r.data),
  updateShift: (id: string, body: Partial<Shift>) => api.patch(`/shifts/${id}`, body).then((r) => r.data),
  createReason: (body: Partial<StoppageReason>) => api.post("/stoppage-reasons", body).then((r) => r.data),
  updateReason: (id: string, body: Partial<StoppageReason>) => api.patch(`/stoppage-reasons/${id}`, body).then((r) => r.data),
  createUser: (body: Record<string, unknown>) => api.post("/users", body).then((r) => r.data),
  updateUser: (id: string, body: Record<string, unknown>) => api.patch(`/users/${id}`, body).then((r) => r.data),
};

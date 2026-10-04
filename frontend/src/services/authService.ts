import type { User } from "../types";
import { api, setToken } from "./api/client";

export const authService = {
  async login(username: string, password: string): Promise<void> {
    const { data } = await api.post<{ access_token: string }>("/auth/login", { username, password });
    setToken(data.access_token);
  },
  async me(): Promise<User> {
    const { data } = await api.get<User>("/auth/me");
    return data;
  },
  logout(): void {
    setToken(null);
  },
};

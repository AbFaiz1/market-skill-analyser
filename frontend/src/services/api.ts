import axios, { AxiosError } from "axios";
import type {
  AuthTokens,
  DashboardStats,
  Job,
  RecommendationsOut,
  RoleComparison,
  Skill,
  TrendSnapshot,
  User,
} from "@/types";

const BASE_URL = (import.meta as any).env.VITE_API_BASE || "http://127.0.0.1:8000";

const api = axios.create({ baseURL: BASE_URL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err: AxiosError) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const authService = {
  register: (data: { email: string; password: string; name?: string; role?: string }) =>
    api.post<User>("/auth/register", data),
  login: (data: { username: string; password: string }) =>
    api.post<AuthTokens>("/auth/login", data, { headers: { "Content-Type": "application/x-www-form-urlencoded" } }),
  me: () => api.get<User>("/auth/me"),
};

export const jobsService = {
  list: (params?: { skip?: number; limit?: number; role?: string }) =>
    api.get<Job[]>("/jobs/", { params }),
  create: (data: any) => api.post<Job>("/jobs/", data),
  get: (id: number) => api.get<Job>(`/jobs/${id}`),
  extract: (id: number) => api.post(`/jobs/${id}/extract`),
  topSkills: (limit = 20) => api.get<Skill[]>("/jobs/skills/top", { params: { limit } }),
};

export const skillsService = {
  list: (skip = 0, limit = 100) => api.get<Skill[]>("/skills/", { params: { skip, limit } }),
  create: (data: any) => api.post<Skill>("/skills/", data),
};

export const trendsService = {
  snapshot: (period_start: string, period_end: string) =>
    api.post<TrendSnapshot[]>("/trends/snapshot", {}, { params: { period_start, period_end } }),
  latest: (limit = 50) => api.get<TrendSnapshot[]>("/trends/latest", { params: { limit } }),
  trending: (limit = 20, label?: string) =>
    api.get<Skill[]>("/trends/skills/trending", { params: { limit, label } }),
  history: (skillId: number, months = 6) =>
    api.get(`/trends/skills/${skillId}/history`, { params: { months } }),
};

export const rolesService = {
  list: () => api.get<Array<{ role: string; count: number }>>("/roles/list"),
  clusters: () => api.get<Array<{ role: string; cluster: number }>>("/roles/clusters"),
  compare: (roleA: string, roleB: string) =>
    api.get<RoleComparison>("/roles/compare", { params: { role_a: roleA, role_b: roleB } }),
};

export const recommendService = {
  get: (targetRole?: string, topN = 10) =>
    api.get<RecommendationsOut>("/recommend/", { params: { target_role: targetRole, top_n: topN } }),
  allSkills: () => api.get<Array<{ id: number; name: string; category?: string }>>("/recommend/skills"),
};

export const dashboardService = {
  stats: (limit = 10) => api.get<DashboardStats>("/dashboard/stats", { params: { limit } }),
};

export const ingestService = {
  mock: (limit = 20) => api.post(`/ingest/mock?limit=${limit}`),
};

export default api;

export interface Skill {
  id: number;
  name: string;
  category?: string;
  demand_score?: number;
  trend_label?: string;
  job_count?: number;
}

export interface Job {
  id: number;
  title: string;
  company?: string;
  location?: string;
  description?: string;
  job_role?: string;
  industry?: string;
  source?: string;
  scraped_at: string;
  is_processed: boolean;
  skills: string[];
}

export interface TrendSnapshot {
  id: number;
  skill_id: number;
  period_start: string;
  period_end: string;
  demand_score: number;
  trend_label: string;
  job_count: number;
}

export interface User {
  id: number;
  email: string;
  name?: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface Profile {
  current_skills: string[];
  target_role?: string;
  experience_level?: string;
  preferred_industry?: string;
}

export interface Recommendation {
  skill: string;
  reason: string;
  priority: string;
  demand_score: number;
  trend_label: string;
}

export interface RecommendationsOut {
  target_role: string;
  current_skills: string[];
  recommendations: Recommendation[];
}

export interface RoleComparison {
  role_a: string;
  role_b: string;
  role_a_skills: Array<{ skill: string; demand_score: number }>;
  role_b_skills: Array<{ skill: string; demand_score: number }>;
  common_skills: string[];
  role_a_only: string[];
  role_b_only: string[];
  match_percentage: number;
}

export interface DashboardStats {
  total_jobs: number;
  total_skills: number;
  top_skills: Skill[];
  emerging_skills: Skill[];
  declining_skills: Skill[];
  roles_distribution: Array<{ role: string; count: number }>;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

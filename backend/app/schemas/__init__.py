from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

from app.models import TrendLabel as TrendLabel


# ---------- User / Auth ----------
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    role: str = "job_seeker"


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


# ---------- User Profile ----------
class ProfileBase(BaseModel):
    current_skills: Optional[List[str]] = None
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
    preferred_industry: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    id: int
    user_id: int
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------- Skill ----------
class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None
    synonyms: Optional[List[str]] = None


class SkillCreate(SkillBase):
    pass


class SkillOut(SkillBase):
    id: int

    model_config = {"from_attributes": True}


class SkillWithDemand(SkillOut):
    demand_score: float = 0.0
    trend_label: str = "stable"
    job_count: int = 0


# ---------- Job ----------
class JobBase(BaseModel):
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    job_role: Optional[str] = None
    industry: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    posted_at: Optional[datetime] = None


class JobCreate(JobBase):
    pass


class JobOut(JobBase):
    id: int
    scraped_at: datetime
    is_processed: bool
    skills: List[str] = []

    model_config = {"from_attributes": True}


# ---------- Job Skill ----------
class JobSkillBase(BaseModel):
    job_id: int
    skill_id: int
    confidence: float = 1.0
    frequency_in_jd: int = 1


class JobSkillOut(JobSkillBase):
    id: int

    model_config = {"from_attributes": True}


# ---------- Trend ----------
class TrendSnapshotBase(BaseModel):
    skill_id: int
    period_start: datetime
    period_end: datetime
    demand_score: float
    trend_label: str
    job_count: int


class TrendSnapshotOut(TrendSnapshotBase):
    id: int

    model_config = {"from_attributes": True}


# ---------- Role Comparison ----------
class RoleSkill(BaseModel):
    skill: str
    demand_score: float


class RoleComparison(BaseModel):
    role_a: str
    role_b: str
    role_a_skills: List[RoleSkill]
    role_b_skills: List[RoleSkill]
    common_skills: List[str]
    role_a_only: List[str]
    role_b_only: List[str]
    match_percentage: float


# ---------- Recommendation ----------
class Recommendation(BaseModel):
    skill: str
    reason: str
    priority: str  # high, medium, low
    demand_score: float
    trend_label: str


class RecommendationsOut(BaseModel):
    target_role: str
    current_skills: List[str]
    recommendations: List[Recommendation]


# ---------- Ingest ----------
class IngestResponse(BaseModel):
    jobs_inserted: int
    message: str


# ---------- Dashboard ----------
class DashboardStats(BaseModel):
    total_jobs: int
    total_skills: int
    top_skills: List[SkillWithDemand]
    emerging_skills: List[SkillWithDemand]
    declining_skills: List[SkillWithDemand]
    roles_distribution: List[dict]

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class UserRole(str, enum.Enum):
    student = "student"
    job_seeker = "job_seeker"
    professional = "professional"
    recruiter = "recruiter"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.job_seeker)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    current_skills = Column(Text, nullable=True)  # JSON string list
    target_role = Column(String(255), nullable=True)
    experience_level = Column(String(50), nullable=True)  # entry, mid, senior
    preferred_industry = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=True)  # mock, linkedin, indeed, etc.
    source_url = Column(Text, nullable=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    job_role = Column(String(255), nullable=True)  # e.g. Data Scientist
    industry = Column(String(255), nullable=True)
    posted_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)

    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)  # canonical
    category = Column(String(100), nullable=True)  # programming, cloud, soft, etc.
    synonyms = Column(Text, nullable=True)  # JSON string list

    job_links = relationship("JobSkill", back_populates="skill")


class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    confidence = Column(Float, default=1.0)
    frequency_in_jd = Column(Integer, default=1)

    __table_args__ = (UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),)

    job = relationship("Job", back_populates="skills")
    skill = relationship("Skill", back_populates="job_links")


class TrendLabel(str, enum.Enum):
    in_demand = "in-demand"
    emerging = "emerging"
    declining = "declining"
    stable = "stable"


class TrendSnapshot(Base):
    __tablename__ = "trend_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    demand_score = Column(Float, default=0.0)
    trend_label = Column(Enum(TrendLabel), default=TrendLabel.stable)
    job_count = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("skill_id", "period_start", "period_end", name="uq_trend_window"),
    )

    skill = relationship("Skill")

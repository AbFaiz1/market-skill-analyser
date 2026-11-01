from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models import Job, Skill, JobSkill, TrendSnapshot
from app.schemas import DashboardStats, SkillWithDemand
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/stats", response_model=DashboardStats, tags=["dashboard"])
def dashboard_stats(
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    total_jobs = db.query(Job).count()
    total_skills = db.query(Skill).count()
    top = (
        db.query(Skill, func.count(JobSkill.id).label("cnt"))
        .join(JobSkill, Skill.id == JobSkill.skill_id)
        .group_by(Skill.id, Skill.name)
        .order_by(func.count(JobSkill.id).desc())
        .limit(limit)
        .all()
    )
    top_skills = []
    for skill, cnt in top:
        snap = (
            db.query(TrendSnapshot)
            .filter(TrendSnapshot.skill_id == skill.id)
            .order_by(TrendSnapshot.period_end.desc())
            .first()
        )
        top_skills.append(
            SkillWithDemand(
                id=skill.id,
                name=skill.name,
                category=skill.category,
                synonyms=None,
                demand_score=float(snap.demand_score) if snap else float(cnt),
                trend_label=snap.trend_label.value if snap else "stable",
                job_count=cnt,
            )
        )
    emerging = (
        db.query(Skill, TrendSnapshot)
        .join(TrendSnapshot, Skill.id == TrendSnapshot.skill_id)
        .filter(TrendSnapshot.trend_label == "emerging")
        .order_by(TrendSnapshot.demand_score.desc())
        .limit(limit)
        .all()
    )
    declining = (
        db.query(Skill, TrendSnapshot)
        .join(TrendSnapshot, Skill.id == TrendSnapshot.skill_id)
        .filter(TrendSnapshot.trend_label == "declining")
        .order_by(TrendSnapshot.demand_score.desc())
        .limit(limit)
        .all()
    )
    roles = (
        db.query(Job.job_role, func.count(Job.id).label("cnt"))
        .filter(Job.job_role.isnot(None))
        .group_by(Job.job_role)
        .all()
    )
    return DashboardStats(
        total_jobs=total_jobs,
        total_skills=total_skills,
        top_skills=top_skills,
        emerging_skills=[
            SkillWithDemand(
                id=s.id, name=s.name, category=s.category, synonyms=None,
                demand_score=float(t.demand_score), trend_label=t.trend_label.value,
                job_count=t.job_count,
            )
            for s, t in emerging
        ],
        declining_skills=[
            SkillWithDemand(
                id=s.id, name=s.name, category=s.category, synonyms=None,
                demand_score=float(t.demand_score), trend_label=t.trend_label.value,
                job_count=t.job_count,
            )
            for s, t in declining
        ],
        roles_distribution=[{"role": r, "count": c} for r, c in roles],
    )

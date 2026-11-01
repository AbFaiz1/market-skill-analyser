from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models import Job, Skill, JobSkill
from app.services.trend_service import cluster_roles
from app.schemas import RoleComparison, RoleSkill

router = APIRouter()


@router.get("/compare", response_model=RoleComparison, tags=["roles"])
def compare_roles(
    role_a: str = Query(...),
    role_b: str = Query(...),
    db: Session = Depends(get_db),
):
    def skills_for(role: str):
        rows = (
            db.query(Skill.name, func.count(JobSkill.id).label("cnt"))
            .join(JobSkill, Skill.id == JobSkill.skill_id)
            .join(Job, JobSkill.job_id == Job.id)
            .filter(Job.job_role.ilike(f"%{role}%"))
            .group_by(Skill.id, Skill.name)
            .all()
        )
        total = sum(cnt for _, cnt in rows) or 1
        return {
            name: {
                "skill": name,
                "demand_score": round((cnt / total) * 100, 2),
            }
            for name, cnt in rows
        }

    sa = skills_for(role_a)
    sb = skills_for(role_b)
    set_a = set(sa.keys())
    set_b = set(sb.keys())
    common = sorted(set_a & set_b)
    a_only = sorted(set_a - set_b)
    b_only = sorted(set_b - set_a)
    union = set_a | set_b
    match_pct = round((len(common) / len(union)) * 100, 2) if union else 0.0

    return RoleComparison(
        role_a=role_a,
        role_b=role_b,
        role_a_skills=[RoleSkill(**sa[k]) for k in sorted(sa)],
        role_b_skills=[RoleSkill(**sb[k]) for k in sorted(sb)],
        common_skills=common,
        role_a_only=a_only,
        role_b_only=b_only,
        match_percentage=match_pct,
    )


@router.get("/list", tags=["roles"])
def list_roles(db: Session = Depends(get_db)):
    roles = (
        db.query(Job.job_role, func.count(Job.id).label("cnt"))
        .filter(Job.job_role.isnot(None))
        .group_by(Job.job_role)
        .order_by(func.count(Job.id).desc())
        .all()
    )
    return [{"role": r, "job_count": c} for r, c in roles]


@router.get("/clusters", tags=["roles"])
def role_clusters(db: Session = Depends(get_db)):
    return cluster_roles(db)

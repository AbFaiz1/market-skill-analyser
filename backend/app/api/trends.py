from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.db.database import get_db
from app.models import TrendSnapshot, Skill
from app.services.trend_service import TrendAnalyzer
from app.schemas import TrendSnapshotOut, SkillWithDemand

router = APIRouter()


@router.post("/snapshot", response_model=List[TrendSnapshotOut], tags=["trends"])
def create_snapshot(
    period_start: datetime,
    period_end: datetime,
    db: Session = Depends(get_db),
):
    analyzer = TrendAnalyzer(db)
    return analyzer.snapshot_for_window(period_start, period_end)


@router.get("/latest", response_model=List[TrendSnapshotOut], tags=["trends"])
def latest_trends(limit: int = Query(50, le=200), db: Session = Depends(get_db)):
    analyzer = TrendAnalyzer(db)
    return analyzer.latest_trends(limit)


@router.get("/skills/trending", response_model=List[SkillWithDemand], tags=["trends"])
def trending_skills(
    limit: int = Query(20, le=100),
    label: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):

    # Get latest snapshot per skill
    latest_sub = (
        db.query(TrendSnapshot.skill_id, func.max(TrendSnapshot.period_end).label("max_end"))
        .group_by(TrendSnapshot.skill_id)
        .subquery()
    )
    q = (
        db.query(Skill, TrendSnapshot)
        .join(TrendSnapshot, Skill.id == TrendSnapshot.skill_id)
        .join(
            latest_sub,
            (TrendSnapshot.skill_id == latest_sub.c.skill_id)
            & (TrendSnapshot.period_end == latest_sub.c.max_end),
        )
    )
    if label:
        q = q.filter(TrendSnapshot.trend_label == label)
    rows = q.order_by(desc(TrendSnapshot.demand_score)).limit(limit).all()
    result = []
    for skill, snap in rows:
        result.append(
            SkillWithDemand(
                id=skill.id,
                name=skill.name,
                category=skill.category,
                synonyms=None,
                demand_score=float(snap.demand_score),
                trend_label=snap.trend_label.value,
                job_count=snap.job_count,
            )
        )
    return result


@router.get("/skills/{skill_id}/history", tags=["trends"])
def skill_history(
    skill_id: int,
    months: int = Query(6, le=24),
    db: Session = Depends(get_db),
):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    end = datetime.utcnow()
    start = end - timedelta(days=30 * months)
    rows = (
        db.query(TrendSnapshot)
        .filter(
            TrendSnapshot.skill_id == skill_id,
            TrendSnapshot.period_end >= start,
            TrendSnapshot.period_end <= end,
        )
        .order_by(TrendSnapshot.period_end.asc())
        .all()
    )
    return {
        "skill": skill.name,
        "history": [
            {
                "period_end": r.period_end,
                "demand_score": float(r.demand_score),
                "trend_label": r.trend_label.value,
                "job_count": r.job_count,
            }
            for r in rows
        ],
    }

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models import Job, Skill, JobSkill
from app.schemas import (
    JobCreate, JobOut, SkillOut, SkillCreate, SkillWithDemand,
)
from app.services.nlp_service import SkillExtractor
from app.etl.ingest_service import IngestService

router = APIRouter()
extractor = SkillExtractor()


@router.post("/", response_model=JobOut, tags=["jobs"])
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    db_job = Job(**job.model_dump(), scraped_at=datetime.utcnow(), is_processed=False)
    db.add(db_job)
    db.flush()
    IngestService(db)._extract_and_link(db_job)
    db.commit()
    db.refresh(db_job)
    return _job_out(db_job, db)


@router.get("/", response_model=List[JobOut], tags=["jobs"])
def list_jobs(
    skip: int = 0,
    limit: int = 50,
    role: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Job)
    if role:
        q = q.filter(Job.job_role.ilike(f"%{role}%"))
    jobs = q.offset(skip).limit(limit).all()
    return [_job_out(j, db) for j in jobs]


@router.get("/{job_id}", response_model=JobOut, tags=["jobs"])
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_out(job, db)


@router.post("/{job_id}/extract", tags=["jobs"])
def extract_job_skills(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    IngestService(db)._extract_and_link(job)
    db.commit()
    return {"message": "Skills extracted", "job_id": job_id}


def _job_out(job: Job, db: Session) -> JobOut:
    skill_names = [js.skill.name for js in job.skills]
    return JobOut(
        id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        description=job.description,
        job_role=job.job_role,
        industry=job.industry,
        source=job.source,
        source_url=job.source_url,
        posted_at=job.posted_at,
        scraped_at=job.scraped_at,
        is_processed=job.is_processed,
        skills=skill_names,
    )


# ---------- Skills ----------
@router.get("/skills", response_model=List[SkillOut], tags=["skills"])
def list_skills(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Skill).offset(skip).limit(limit).all()


@router.post("/skills", response_model=SkillOut, tags=["skills"])
def create_skill(skill: SkillCreate, db: Session = Depends(get_db)):
    existing = db.query(Skill).filter(Skill.name == skill.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Skill already exists")
    db_skill = Skill(**skill.model_dump())
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill


@router.get("/skills/top", response_model=List[SkillWithDemand], tags=["skills"])
def top_skills(
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    from app.models import TrendSnapshot

    rows = (
        db.query(Skill, func.count(JobSkill.id).label("cnt"))
        .join(JobSkill, Skill.id == JobSkill.skill_id)
        .group_by(Skill.id, Skill.name, Skill.category, Skill.synonyms)
        .order_by(func.count(JobSkill.id).desc())
        .limit(limit)
        .all()
    )
    result = []
    for skill, cnt in rows:
        snap = (
            db.query(TrendSnapshot)
            .filter(TrendSnapshot.skill_id == skill.id)
            .order_by(TrendSnapshot.period_end.desc())
            .first()
        )
        result.append(
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
    return result

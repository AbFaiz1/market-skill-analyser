from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict

import numpy as np
from sklearn.cluster import KMeans
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Job, Skill, JobSkill, TrendSnapshot
from app.schemas import TrendLabel


class TrendAnalyzer:
    """Computes demand scores and classifies skill trends."""

    def __init__(self, db: Session):
        self.db = db

    def compute_demand_score(
        self, skill_id: int, period_start: datetime, period_end: datetime
    ) -> Tuple[float, int]:
        total_jobs = (
            self.db.query(Job)
            .filter(Job.posted_at >= period_start, Job.posted_at <= period_end)
            .count()
        )
        if total_jobs == 0:
            return 0.0, 0
        job_ids_sub = (
            self.db.query(JobSkill.job_id)
            .join(Job, JobSkill.job_id == Job.id)
            .filter(
                JobSkill.skill_id == skill_id,
                Job.posted_at >= period_start,
                Job.posted_at <= period_end,
            )
            .distinct()
            .subquery()
        )
        skill_jobs = self.db.query(func.count(job_ids_sub.c.job_id)).scalar() or 0
        score = round((skill_jobs / total_jobs) * 100, 2)
        return score, int(skill_jobs)

    def classify_trend(
        self, skill_id: int, history: List[Tuple[datetime, float]]
    ) -> str:
        if len(history) == 0:
            return TrendLabel.stable
        history_sorted = sorted(history, key=lambda x: x[0])
        scores = [s for _, s in history_sorted]
        last = scores[-1]
        # Single snapshot window: classify by demand level
        if len(history) == 1:
            if last >= 20:
                return TrendLabel.in_demand
            if last > 0:
                return TrendLabel.emerging
            return TrendLabel.stable
        first = scores[0]
        if first == 0 and all(s == 0 for s in scores[:-1]):
            return TrendLabel.emerging if last > 0 else TrendLabel.stable
        if first == 0:
            return TrendLabel.emerging if last > 0 else TrendLabel.stable
        change_pct = (last - first) / max(first, 0.001)
        if change_pct >= 0.25:
            return TrendLabel.in_demand
        if change_pct <= -0.25:
            return TrendLabel.declining
        if last >= 20:
            return TrendLabel.in_demand
        return TrendLabel.stable

    def snapshot_for_window(
        self, period_start: datetime, period_end: datetime
    ) -> List[TrendSnapshot]:
        # Replace existing snapshots for this window
        self.db.query(TrendSnapshot).filter(
            TrendSnapshot.period_start == period_start,
            TrendSnapshot.period_end == period_end,
        ).delete()
        self.db.commit()
        snapshots: List[TrendSnapshot] = []
        skills = self.db.query(Skill).all()
        for skill in skills:
            demand_score, job_count = self.compute_demand_score(
                skill.id, period_start, period_end
            )
            # Build short history from prior windows for trend label
            prior = []
            delta = period_end - period_start
            for i in range(1, 4):
                ps = period_start - i * delta
                pe = period_end - i * delta
                s, _ = self.compute_demand_score(skill.id, ps, pe)
                prior.append((ps, s))
            prior.append((period_end, demand_score))
            label = self.classify_trend(skill.id, prior)
            snapshots.append(
                TrendSnapshot(
                    skill_id=skill.id,
                    period_start=period_start,
                    period_end=period_end,
                    demand_score=demand_score,
                    trend_label=label,
                    job_count=job_count,
                )
            )
        self.db.add_all(snapshots)
        self.db.commit()
        for s in snapshots:
            self.db.refresh(s)
        return snapshots

    def latest_trends(self, limit: int = 50) -> List[TrendSnapshot]:
        return (
            self.db.query(TrendSnapshot)
            .order_by(TrendSnapshot.period_end.desc())
            .limit(limit)
            .all()
        )


def cluster_roles(db: Session, n_clusters: int = 5) -> List[Dict]:
    """Cluster job roles by skill profile using KMeans."""
    jobs = db.query(Job).filter(Job.is_processed == True).all()  # noqa: E712
    if not jobs:
        return []
    role_skill_matrix = defaultdict(lambda: defaultdict(int))
    all_skills = set()
    for job in jobs:
        role = job.job_role or "Other"
        for js in job.skills:
            role_skill_matrix[role][js.skill_id] += 1
            all_skills.add(js.skill_id)
    if not all_skills:
        return []
    skill_list = sorted(all_skills)
    roles = sorted(role_skill_matrix.keys())
    X = np.array(
        [[role_skill_matrix[r].get(s, 0) for s in skill_list] for r in roles],
        dtype=float,
    )
    n = min(n_clusters, len(roles))
    if n < 2:
        return [{"role": r, "cluster": 0} for r in roles]
    kmeans = KMeans(n_clusters=n, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    return [{"role": roles[i], "cluster": int(labels[i])} for i in range(len(roles))]

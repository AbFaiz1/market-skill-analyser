from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Job, Skill, JobSkill, UserProfile
from app.services.nlp_service import SkillExtractor
from app.schemas import Recommendation, RecommendationsOut


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.extractor = SkillExtractor()

    def recommend_for_user(
        self, user_id: int, top_n: int = 10
    ) -> RecommendationsOut:
        profile = (
            self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        )
        target_role = profile.target_role if profile else None
        current_skills = []
        if profile and profile.current_skills:
            try:
                import json

                current_skills = json.loads(profile.current_skills)
            except Exception:
                current_skills = []
        if not target_role:
            target_role = "Software Engineer"

        role_skills = self._top_skills_for_role(target_role, top_n * 2)
        current_set = set(s.lower() for s in current_skills)

        recommendations: List[Recommendation] = []
        for rs in role_skills:
            skill_name = rs["skill"]
            if skill_name.lower() in current_set:
                continue
            rec = Recommendation(
                skill=skill_name,
                reason=f"Required for {target_role} roles",
                priority="high" if rs["demand_score"] > 20 else "medium",
                demand_score=rs["demand_score"],
                trend_label=rs["trend_label"],
            )
            recommendations.append(rec)
            if len(recommendations) >= top_n:
                break

        # Fallback: popular trending skills
        if len(recommendations) < top_n:
            trending = self._top_trending_skills(top_n - len(recommendations))
            existing = {r.skill for r in recommendations}
            for ts in trending:
                if ts["skill"].lower() in current_set or ts["skill"] in existing:
                    continue
                recommendations.append(
                    Recommendation(
                        skill=ts["skill"],
                        reason="High market demand",
                        priority="medium",
                        demand_score=ts["demand_score"],
                        trend_label=ts["trend_label"],
                    )
                )

        return RecommendationsOut(
            target_role=target_role,
            current_skills=current_skills,
            recommendations=recommendations[:top_n],
        )

    def _top_skills_for_role(self, role: str, limit: int) -> List[Dict]:
        skills = (
            self.db.query(Skill.name, func.count(JobSkill.id).label("cnt"))
            .join(JobSkill, Skill.id == JobSkill.skill_id)
            .join(Job, JobSkill.job_id == Job.id)
            .filter(Job.job_role.ilike(f"%{role}%"))
            .group_by(Skill.id, Skill.name)
            .order_by(func.count(JobSkill.id).desc())
            .limit(limit)
            .all()
        )
        result = []
        for name, cnt in skills:
            snap = (
                self.db.query(__import__("app.models", fromlist=["TrendSnapshot"]).TrendSnapshot)
                .join(Skill)
                .filter(Skill.name == name)
                .order_by(__import__("app.models", fromlist=["TrendSnapshot"]).TrendSnapshot.period_end.desc())
                .first()
            )
            result.append(
                {
                    "skill": name,
                    "demand_score": float(snap.demand_score) if snap else 10.0,
                    "trend_label": snap.trend_label.value if snap else "stable",
                }
            )
        return result

    def _top_trending_skills(self, limit: int) -> List[Dict]:
        from app.models import TrendSnapshot

        snaps = (
            self.db.query(TrendSnapshot, Skill.name)
            .join(Skill, TrendSnapshot.skill_id == Skill.id)
            .order_by(TrendSnapshot.period_end.desc(), TrendSnapshot.demand_score.desc())
            .limit(limit)
            .all()
        )
        seen = set()
        result = []
        for snap, name in snaps:
            if name in seen:
                continue
            seen.add(name)
            result.append(
                {
                    "skill": name,
                    "demand_score": float(snap.demand_score),
                    "trend_label": snap.trend_label.value,
                }
            )
        return result

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import User
from app.services.recommend_service import RecommendationService
from app.api.auth import get_current_user
from app.schemas import RecommendationsOut

router = APIRouter()


@router.get("/", response_model=RecommendationsOut, tags=["recommend"])
def recommendations(
    target_role: str = Query(None),
    top_n: int = Query(10, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if target_role:
        profile = (
            db.query(__import__("app.models", fromlist=["UserProfile"]).UserProfile)
            .filter(__import__("app.models", fromlist=["UserProfile"]).UserProfile.user_id == current_user.id)
            .first()
        )
        if not profile:
            from app.models import UserProfile

            profile = UserProfile(
                user_id=current_user.id, target_role=target_role
            )
            db.add(profile)
            db.commit()
        else:
            profile.target_role = target_role
            db.commit()
    svc = RecommendationService(db)
    return svc.recommend_for_user(current_user.id, top_n=top_n)


@router.get("/skills", tags=["recommend"])
def all_skills(db: Session = Depends(get_db)):
    from app.models import Skill

    rows = db.query(Skill).all()
    return [{"id": s.id, "name": s.name, "category": s.category} for s in rows]

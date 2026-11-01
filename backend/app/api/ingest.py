from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.etl.ingest_service import IngestService, MOCK_JOBS
from app.schemas import IngestResponse
from app.api.auth import get_current_user

router = APIRouter()


@router.post("/mock", response_model=IngestResponse, tags=["ingest"])
def ingest_mock(
    limit: int = Query(20, le=len(MOCK_JOBS)),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = IngestService(db)
    inserted = svc.ingest_mock(limit=limit)
    return IngestResponse(jobs_inserted=inserted, message=f"Inserted {inserted} mock jobs")


@router.post("/run", tags=["ingest"])
def run_etl(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    svc = IngestService(db)
    inserted = svc.ingest_mock(limit=len(MOCK_JOBS))
    return {"jobs_inserted": inserted, "message": "ETL complete"}

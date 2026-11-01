from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import engine, Base
from app.api import jobs, trends, roles, recommend, auth, ingest, dashboard

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(trends.router, prefix="/trends", tags=["trends"])
app.include_router(roles.router, prefix="/roles", tags=["roles"])
app.include_router(recommend.router, prefix="/recommend", tags=["recommend"])
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])


@app.get("/", tags=["health"])
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy"}

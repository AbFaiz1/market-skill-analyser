import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db

TEST_DB_URL = "sqlite:///./test_skill_trend.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_register_and_login():
    r = client.post(
        "/auth/register",
        json={"email": "a@b.com", "password": "secret123", "name": "A", "role": "student"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["email"] == "a@b.com"

    r = client.post("/auth/login", data={"username": "a@b.com", "password": "secret123"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password():
    client.post(
        "/auth/register",
        json={"email": "c@d.com", "password": "secret123", "name": "C"},
    )
    r = client.post("/auth/login", data={"username": "c@d.com", "password": "wrong"})
    assert r.status_code == 401


def test_ingest_and_jobs():
    # register + login
    client.post(
        "/auth/register",
        json={"email": "e@f.com", "password": "secret123", "name": "E"},
    )
    lr = client.post("/auth/login", data={"username": "e@f.com", "password": "secret123"})
    token = lr.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post("/ingest/mock?limit=5", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["jobs_inserted"] > 0

    r = client.get("/jobs/?limit=10")
    assert r.status_code == 200
    jobs = r.json()
    assert len(jobs) > 0
    assert jobs[0]["skills"]  # skills extracted


def test_skills_top():
    client.post(
        "/auth/register",
        json={"email": "g@h.com", "password": "secret123", "name": "G"},
    )
    lr = client.post("/auth/login", data={"username": "g@h.com", "password": "secret123"})
    token = lr.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/ingest/mock?limit=10", headers=headers)

    r = client.get("/jobs/skills/top?limit=5")
    assert r.status_code == 200
    skills = r.json()
    assert len(skills) > 0
    assert skills[0]["name"]


def test_snapshot_and_trending():
    client.post(
        "/auth/register",
        json={"email": "i@j.com", "password": "secret123", "name": "I"},
    )
    lr = client.post("/auth/login", data={"username": "i@j.com", "password": "secret123"})
    token = lr.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/ingest/mock?limit=10", headers=headers)

    r = client.post(
        "/trends/snapshot?period_start=2026-01-01T00:00:00&period_end=2026-12-31T23:59:59",
        headers=headers,
    )
    assert r.status_code == 200, r.text
    snaps = r.json()
    assert len(snaps) > 0

    r = client.get("/trends/skills/trending?limit=5")
    assert r.status_code == 200
    trending = r.json()
    assert len(trending) > 0


def test_roles_compare():
    client.post(
        "/auth/register",
        json={"email": "k@l.com", "password": "secret123", "name": "K"},
    )
    lr = client.post("/auth/login", data={"username": "k@l.com", "password": "secret123"})
    token = lr.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/ingest/mock?limit=10", headers=headers)

    r = client.get(
        "/roles/compare?role_a=Data Scientist&role_b=Full Stack Developer"
    )
    assert r.status_code == 200
    data = r.json()
    assert "match_percentage" in data
    assert "common_skills" in data

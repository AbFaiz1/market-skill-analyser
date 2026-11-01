# AI-Based Job Market Skill Trend Analyzer — Phase-Wise Roadmap

## Phase 0 — Setup & Foundation (Week 1)
**Goal:** Initialize project, environment, and core configuration.

**Tasks:**
- Initialize git repo, folder structure (backend/, frontend/, docs/, scripts/, tests/)
- Python venv + requirements.txt (FastAPI, SQLAlchemy, spaCy, scikit-learn, pandas, nltk, fuzzywuzzy, python-jose, passlib, python-dotenv, pytest)
- Node + npm init, frontend with Vite + React + TypeScript + Tailwind + Recharts + Lucide React
- `.env` template + config module (settings via pydantic-settings)
- Dockerfile (backend) + docker-compose.yml (backend + db)

**Exit Criteria:** `pip install -r requirements.txt` and `npm install` succeed; `uvicorn` health endpoint returns 200; `npm run dev` starts frontend.

---

## Phase 1 — Data Model & Ingestion Pipeline (Week 2)
**Goal:** Persist job postings and run ETL from raw text to structured records.

**Tasks:**
- SQLAlchemy models: User, UserProfile, Job, Skill, JobSkill, TrendSnapshot
- Alembic migrations + SQLite (dev) / PostgreSQL (prod) support
- Job scraper module (BeautifulSoup + requests) with retry/timeout/user-agent
- Sample/mock job dataset (500+ postings across tech, data, design, marketing roles) so system works without live scraping
- ETL: raw HTML → clean text → store in `Job` table
- Unit tests for models + scraper

**Exit Criteria:** Jobs can be ingested (mock + optional live); DB schema created via Alembic; tests pass.

---

## Phase 2 — NLP Skill Extraction & Normalization (Week 3)
**Goal:** Extract canonical skills from job descriptions.

**Tasks:**
- spaCy `en_core_web_sm` NER + custom skill gazetteer (500+ canonical skills: programming, frameworks, tools, soft skills, cloud, databases)
- Text cleaner: strip HTML, lowercase, remove stopwords, punctuation handling
- Skill extractor: NER entities + keyword matching + TF-IDF weighting
- Normalizer: fuzzy matching + synonym map → canonical skill names
- Confidence scoring per extracted skill per job
- Store results in `JobSkill` table

**Exit Criteria:** Given a JD, system returns normalized skill list with confidence; synonyms (e.g. "js", "javascript") map to one canonical skill.

---

## Phase 3 — Trend Analysis & ML Models (Week 4)
**Goal:** Classify skills as in-demand / emerging / declining; cluster roles.

**Tasks:**
- Demand score computation per skill per time window (monthly)
- Trend classifier: slope-based (in-demand / emerging / declining)
- KMeans clustering of job roles by skill profile
- TrendSnapshot table populated per window
- ML module with retrain/save/load (joblib)
- Unit tests for trend labels + clustering output

**Exit Criteria:** API can return trend label + demand score for any skill over a date range; roles cluster sensibly.

---

## Phase 4 — REST API & Recommendations (Week 5)
**Goal:** Expose all features via versioned REST API.

**Tasks:**
- FastAPI routers: `/jobs`, `/skills`, `/trends`, `/roles`, `/recommend`, `/auth`, `/ingest`
- Pydantic request/response schemas
- JWT auth (register/login), bcrypt passwords, protected routes
- Recommendation engine: content-based (target role → missing skills) + popularity fallback
- Role comparison endpoint (skill overlap/gap between two roles)
- Pagination, filtering, sorting, CORS, error handling
- API tests (pytest + httpx)

**Exit Criteria:** All endpoints return correct status codes + shaped JSON; auth protects write endpoints.

---

## Phase 5 — Frontend Web Application (Week 6)
**Goal:** Build the user-facing React app.

**Tasks:**
- Vite + React + TypeScript + Tailwind CSS setup
- Layout: navbar, sidebar, responsive grid
- Pages: Dashboard, Skills/Trends, Role Comparison, Recommendations, Auth (Login/Register)
- Recharts: line (trend over time), bar (top skills), pie (role distribution), word-cloud-ish skill tags
- Recommendations panel: target role → learn these skills
- Role comparison: side-by-side skill tables with match % 
- API client (axios/fetch) with JWT interceptors
- Loading/error/empty states

**Exit Criteria:** Frontend connects to backend; all pages render; charts display real trend data.

---

## Phase 6 — Polish, Testing & Deployment (Week 7)
**Goal:** Harden, document, and ship.

**Tasks:**
- Integration tests (frontend → backend critical paths)
- Lint: ruff (python) + eslint + prettier (frontend); typecheck: mypy + tsc
- README with setup/run instructions, API docs (FastAPI auto /docs)
- Docker Compose prod profile (PostgreSQL + Nginx)
- Seed script for demo data
- Final end-to-end smoke test

**Exit Criteria:** `docker compose up` runs full stack; lint/typecheck clean; E2E smoke test passes.

---

## Deliverables Summary

| Phase | Deliverable |
|-------|-------------|
| 0 | Repo, env, configs, Docker |
| 1 | DB models, migrations, scraper, ETL, mock data |
| 2 | NLP skill extractor + normalizer |
| 3 | Trend classifier + role clustering |
| 4 | FastAPI REST API + auth + recommendations |
| 5 | React frontend + visualizations |
| 6 | Tests, lint, Docker, README, E2E pass |

## Success Criteria (100% Working)
- System starts with one command (`docker compose up` or `make run`)
- Works offline with seeded mock data (no external scraping required)
- Extracts & normalizes skills accurately
- Shows in-demand / emerging / declining trends with charts
- Compares roles and gives personalized recommendations
- All lint, typecheck, and tests pass

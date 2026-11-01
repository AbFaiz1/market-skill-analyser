# AI-Based Job Market Skill Trend Analyzer

A web-based AI system that extracts skills from job descriptions, analyzes skill demand and trends, compares requirements across job roles, and provides visual reports and personalized skill recommendations.

## Domains
Artificial Intelligence, Machine Learning, Natural Language Processing, Data Analytics, Web Application Development.

## Architecture
- **Backend:** FastAPI (Python), SQLAlchemy, spaCy/NLTK, scikit-learn
- **Frontend:** React + TypeScript + Vite + Tailwind CSS + Recharts
- **Storage:** SQLite (dev) / PostgreSQL (prod)
- **AI/NLP:** Skill extraction (NER + gazetteer + TF-IDF), normalization, trend classification (in-demand / emerging / declining), KMeans role clustering, content-based recommendations

## Project Structure
```
backend/          # FastAPI app + ML/NLP services + ETL + tests
frontend/         # React + TypeScript SPA
ARCHITECTURE.md   # System design
ROADMAP.md        # Phase-wise plan
docker-compose.yml
README.md
```

## Quick Start (Local, no Docker)

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('stopwords')"
python -m uvicorn app.main:app --reload   # http://127.0.0.1:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                               # http://localhost:5173
```

### One-command (Docker)
```bash
docker compose up --build
# Backend: http://localhost:8000   (docs at /docs)
# Frontend: run `npm run dev` separately or serve the built dist
```

## Demo Data
The system ships with 10+ mock job postings across Data Scientist, Full Stack, Frontend, DevOps, ML Engineer, Data Analyst, Backend, Cybersecurity, Product Manager, and Cloud Architect roles. It works offline without scraping.

After starting the backend:
1. `POST /ingest/mock?limit=10` (auth required) — seed mock jobs
2. `POST /trends/snapshot?period_start=...&period_end=...` — build trend snapshots
3. Visit `/dashboard`, `/skills`, `/roles`, `/recommend` in the frontend

## API Docs
FastAPI auto-docs: `http://127.0.0.1:8000/docs` (Swagger UI)

## Key Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register user |
| POST | /auth/login | Login (returns JWT) |
| GET | /jobs/ | List jobs (with extracted skills) |
| POST | /ingest/mock | Seed mock job data |
| POST | /trends/snapshot | Build trend snapshots for a window |
| GET | /trends/skills/trending | Top skills by demand/trend label |
| GET | /roles/compare?role_a=&role_b= | Compare two roles |
| GET | /recommend/?target_role= | Personalized skill recommendations |
| GET | /dashboard/stats | KPI + chart data |

## Lint / Typecheck
```bash
# Backend
cd backend
ruff check .
mypy app

# Frontend
cd frontend
npm run lint   # (eslint not configured; tsc is used)
npx tsc --noEmit
```

## Testing
```bash
cd backend
pytest
```

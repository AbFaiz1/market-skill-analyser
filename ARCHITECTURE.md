# AI-Based Job Market Skill Trend Analyzer — System Architecture

## 1. Project Overview

**Objective:** Develop an AI-based system that analyzes job postings to identify in-demand, emerging, and declining skills across job roles and industries, helping students and job seekers understand current market requirements.

**Outcome:** A web-based AI system that extracts skills from job descriptions, analyzes skill demand and trends, compares requirements across job roles, and provides visual reports and personalized skill recommendations.

**Domains:** Artificial Intelligence, Machine Learning, Natural Language Processing, Data Analytics, Web Application Development.

---

## 2. High-Level Architecture (Layered, Modular)

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER (Frontend)                 │
│  React + TypeScript + Vite + Tailwind + Recharts            │
│  • Dashboard, Skill Trends, Role Comparison, Recommendations│
└─────────────────────────────────────────────────────────────┘
                           │ HTTPS/JSON
┌─────────────────────────────────────────────────────────────┐
│                    API LAYER (Backend)                      │
│  FastAPI (Python) + Pydantic + SQLAlchemy                   │
│  • REST endpoints: jobs, skills, trends, roles, users       │
│  • Authentication (JWT), rate limiting, CORS                │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                 AI / NLP / ML ENGINE LAYER                  │
│  spaCy, NLTK, scikit-learn, Pandas                          │
│  • Skill extraction (NER + keyword + TF-IDF)                │
│  • Skill normalization & synonym mapping                    │
│  • Trend classification: in-demand / emerging / declining   │
│  • Clustering (KMeans) for role-based skill grouping        │
│  • Collaborative/content-based recommendations              │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                 DATA / INGESTION LAYER                      │
│  Scrapers (BeautifulSoup, requests, Selenium fallback)      │
│  • Job posting ingestion from multiple sources              │
│  • Raw → cleaned → structured ETL pipeline                  │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                            │
│  SQLite (dev) / PostgreSQL (prod) via SQLAlchemy            │
│  • Jobs, Skills, JobSkills, Trends, Users, UserProfiles     │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Component Details

### 3.1 Frontend (React + TypeScript)
| Module | Responsibility |
|--------|----------------|
| Auth | Login/register, JWT storage, protected routes |
| Dashboard | KPI cards: total jobs, top skills, emerging/declining counts |
| Skill Trends | Time-series charts of skill demand (Recharts) |
| Role Comparison | Side-by-side skill requirements across roles |
| Recommendations | Personalized skill suggestions based on user profile |
| Visuals | Bar, line, pie, word-cloud style charts |

### 3.2 Backend (FastAPI)
| Module | Responsibility |
|--------|----------------|
| `jobs` | CRUD + search/filter job postings |
| `skills` | Extract, normalize, list skills with frequency |
| `trends` | Compute demand score, trend classification per time window |
| `roles` | Compare skill requirements across job roles |
| `recommend` | Personalized skill recommendations |
| `ingest` | Trigger scraping + ETL pipeline |
| `auth` | JWT issue/verify, password hashing (bcrypt) |

### 3.3 AI / NLP Engine
| Component | Tech | Responsibility |
|-----------|------|----------------|
| Text cleaner | NLTK + regex | HTML stripping, lowercasing, stopword removal |
| Skill extractor | spaCy NER + custom gazetteer | Extract skill entities from JDs |
| Normalizer | fuzzywuzzy + synonym map | Map variants to canonical skill names |
| Demand scorer | TF-IDF + frequency | Compute per-skill demand score per period |
| Trend classifier | Heuristic + slope | in-demand / emerging / declining |
| Clusterer | scikit-learn KMeans | Group roles by skill profile |
| Recommender | Content-based + collaborative | Suggest skills to learn |

### 3.4 Data Model (SQLAlchemy)

```
User (id, email, password_hash, name, role, created_at)
UserProfile (id, user_id, current_skills[], target_role, experience_level)
Job (id, source, source_url, title, company, location, description,
     raw_text, posted_at, scraped_at, job_role, industry)
Skill (id, name, canonical_name, category, synonyms[])
JobSkill (job_id, skill_id, confidence, frequency_in_jd)
TrendSnapshot (id, skill_id, period_start, period_end, demand_score,
               trend_label, job_count)
```

---

## 4. Data Flow

1. **Ingestion:** Scrapers fetch raw job postings → stored in `Job` table.
2. **ETL:** Clean text → NLP skill extraction → `JobSkill` links with confidence.
3. **Analysis:** Aggregate skill frequencies per time window → `TrendSnapshot` with demand score + trend label.
4. **API:** Frontend queries `/skills`, `/trends`, `/roles/compare`, `/recommend`.
5. **UI:** Render charts, tables, and personalized recommendations.

---

## 5. Trend Classification Logic

- **In-demand:** demand_score rising or stable-high over recent windows; appears in many current postings.
- **Emerging:** low historical frequency, sharp recent increase; new to market.
- **Declining:** high historical frequency, sharp recent decrease; fading from postings.

Demand score = (skill postings in window / total postings in window) × 100.

---

## 6. Security & Reliability

- JWT-based stateless auth; bcrypt password hashing.
- CORS restricted to frontend origin.
- Input validation via Pydantic schemas.
- Graceful degradation: if NLP model unavailable, fall back to keyword gazetteer.
- Mock/sample dataset included so system works without live scraping.

---

## 7. Deployment

- **Dev:** `uvicorn` + SQLite + `vite` dev server.
- **Prod:** Docker Compose (FastAPI + PostgreSQL + Nginx + React build).
- Environment variables via `.env`.

import json
from datetime import datetime
from typing import List, Dict

from sqlalchemy.orm import Session

from app.models import Job, Skill, JobSkill
from app.services.nlp_service import SkillExtractor


MOCK_JOBS: List[Dict] = [
    {
        "title": "Senior Data Scientist",
        "company": "TechCorp",
        "location": "Bangalore, India",
        "description": "We are looking for a Senior Data Scientist with expertise in Python, machine learning, deep learning, TensorFlow, PyTorch, SQL, and AWS. Experience with Pandas, NumPy, scikit-learn, and data visualization using Tableau or Power BI is required. Strong communication and problem-solving skills.",
        "job_role": "Data Scientist",
        "industry": "Technology",
        "source": "mock",
    },
    {
        "title": "Full Stack Developer",
        "company": "WebSolutions",
        "location": "Remote",
        "description": "Full stack developer role requiring JavaScript, TypeScript, React, Node.js, Express, MongoDB, PostgreSQL, Docker, and AWS. Knowledge of CI/CD, Git, and Agile methodologies. REST and GraphQL API development experience.",
        "job_role": "Full Stack Developer",
        "industry": "Technology",
        "source": "mock",
    },
    {
        "title": "Frontend Engineer",
        "company": "UIStudio",
        "location": "New York, USA",
        "description": "Frontend engineer with React, TypeScript, HTML, CSS, Tailwind CSS, Figma, and UI/UX design. Experience with state management, responsive design, and accessibility. Strong teamwork and communication skills.",
        "job_role": "Frontend Developer",
        "industry": "Technology",
        "source": "mock",
    },
    {
        "title": "DevOps Engineer",
        "company": "CloudOps",
        "location": "London, UK",
        "description": "DevOps engineer experienced with AWS, Docker, Kubernetes, Terraform, Jenkins, GitHub Actions, CI/CD pipelines, Linux, and monitoring. Infrastructure as code and cloud security.",
        "job_role": "DevOps Engineer",
        "industry": "Technology",
        "source": "mock",
    },
    {
        "title": "Machine Learning Engineer",
        "company": "AI Labs",
        "location": "San Francisco, USA",
        "description": "ML Engineer to build and deploy machine learning models using Python, PyTorch, TensorFlow, scikit-learn, AWS SageMaker, Docker, and Kubernetes. Experience with MLOps, data pipelines, and model monitoring.",
        "job_role": "Machine Learning Engineer",
        "industry": "Artificial Intelligence",
        "source": "mock",
    },
    {
        "title": "Data Analyst",
        "company": "Insightly",
        "location": "Remote",
        "description": "Data Analyst with SQL, Python, Excel, Tableau, Power BI, statistics, and data visualization. Experience with ETL, data warehousing, Snowflake, and business reporting. Strong problem-solving skills.",
        "job_role": "Data Analyst",
        "industry": "Analytics",
        "source": "mock",
    },
    {
        "title": "Backend Developer",
        "company": "ServerSide Inc",
        "location": "Berlin, Germany",
        "description": "Backend developer with Java, Spring Boot, Python, Django, PostgreSQL, Redis, REST APIs, Git, and Agile. Experience with microservices, Docker, and AWS.",
        "job_role": "Backend Developer",
        "industry": "Technology",
        "source": "mock",
    },
    {
        "title": "Cybersecurity Analyst",
        "company": "SecureNet",
        "location": "Singapore",
        "description": "Cybersecurity analyst with network security, penetration testing, SIEM, incident response, Linux, and risk assessment. Knowledge of compliance and security best practices.",
        "job_role": "Cybersecurity Analyst",
        "industry": "Security",
        "source": "mock",
    },
    {
        "title": "Product Manager",
        "company": "ProductCo",
        "location": "Austin, USA",
        "description": "Product Manager with Agile, Scrum, project management, stakeholder communication, roadmap planning, and data-driven decision making. Experience with SQL and analytics tools.",
        "job_role": "Product Manager",
        "industry": "Technology",
        "source": "mock",
    },
    {
        "title": "Cloud Architect",
        "company": "CloudScale",
        "location": "Remote",
        "description": "Cloud Architect designing AWS and Azure solutions with Terraform, Kubernetes, Docker, and infrastructure as code. Experience with cloud migration, security, and cost optimization.",
        "job_role": "Cloud Architect",
        "industry": "Technology",
        "source": "mock",
    },
]


class IngestService:
    def __init__(self, db: Session):
        self.db = db
        self.extractor = SkillExtractor()

    def ingest_mock(self, limit: int = 50) -> int:
        count = 0
        for data in MOCK_JOBS[:limit]:
            exists = (
                self.db.query(Job)
                .filter(Job.title == data["title"], Job.company == data["company"])
                .first()
            )
            if exists:
                continue
            job = Job(
                title=data["title"],
                company=data["company"],
                location=data.get("location"),
                description=data["description"],
                raw_text=data["description"],
                job_role=data.get("job_role"),
                industry=data.get("industry"),
                source=data.get("source", "mock"),
                source_url=None,
                posted_at=datetime.utcnow(),
                is_processed=False,
            )
            self.db.add(job)
            self.db.flush()
            self._extract_and_link(job)
            count += 1
        self.db.commit()
        return count

    def _extract_and_link(self, job: Job):
        text = job.description or ""
        extracted = self.extractor.extract(text)
        job.is_processed = True
        for entry in extracted:
            skill = (
                self.db.query(Skill).filter(Skill.name == entry["canonical"]).first()
            )
            if not skill:
                skill = Skill(
                    name=entry["canonical"],
                    category=self._category_for(entry["canonical"]),
                    synonyms=json.dumps([entry["skill"]]),
                )
                self.db.add(skill)
                self.db.flush()
            js = JobSkill(
                job_id=job.id,
                skill_id=skill.id,
                confidence=entry["confidence"],
                frequency_in_jd=1,
            )
            self.db.add(js)

    def _category_for(self, skill: str) -> str:
        cats = {
            "Python": "programming", "JavaScript": "programming",
            "TypeScript": "programming", "Java": "programming",
            "C++": "programming", "C#": "programming", "Go": "programming",
            "Rust": "programming", "Swift": "programming", "Kotlin": "programming",
            "PHP": "programming", "Ruby": "programming",
            "SQL": "database", "NoSQL": "database", "PostgreSQL": "database",
            "MySQL": "database", "MongoDB": "database", "Redis": "database",
            "Elasticsearch": "database",
            "HTML": "frontend", "CSS": "frontend", "React": "frontend",
            "Angular": "frontend", "Vue": "frontend", "Node.js": "backend",
            "Django": "backend", "Flask": "backend", "FastAPI": "backend",
            "Spring Boot": "backend", "Express": "backend",
            "AWS": "cloud", "Azure": "cloud", "GCP": "cloud",
            "Docker": "devops", "Kubernetes": "devops", "Terraform": "devops",
            "Git": "tools", "CI/CD": "devops", "Jenkins": "devops",
            "Linux": "tools", "Unix": "tools", "GitHub Actions": "devops",
            "Machine Learning": "ai/ml", "Deep Learning": "ai/ml", "NLP": "ai/ml",
            "Computer Vision": "ai/ml", "TensorFlow": "ai/ml", "PyTorch": "ai/ml",
            "Pandas": "ai/ml", "NumPy": "ai/ml", "Scikit-learn": "ai/ml",
            "Tableau": "analytics", "Power BI": "analytics", "Excel": "analytics",
            "Statistics": "analytics", "Data Analysis": "analytics",
            "Data Engineering": "analytics", "ETL": "analytics",
            "API": "backend", "GraphQL": "backend", "Microservices": "backend",
            "REST": "backend", "Agile": "soft", "Scrum": "soft",
            "Project Management": "soft", "Communication": "soft",
            "Leadership": "soft", "Problem Solving": "soft",
            "Teamwork": "soft", "Critical Thinking": "soft",
            "Time Management": "soft", "PySpark": "analytics",
            "Hadoop": "analytics", "Kafka": "analytics", "Snowflake": "analytics",
            "Databricks": "analytics", "Airflow": "analytics",
            "Figma": "frontend", "Adobe XD": "frontend", "Sketch": "frontend",
            "UI/UX": "frontend", "Cybersecurity": "security",
            "Penetration Testing": "security", "DevOps": "devops",
            "Selenium": "testing", "Cypress": "testing", "Jest": "testing",
            "PyTest": "testing", "Looker": "analytics",
        }
        return cats.get(skill, "other")

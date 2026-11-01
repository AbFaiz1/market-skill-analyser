import re
from typing import List, Dict, Optional

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from fuzzywuzzy import process, fuzz
import spacy

from app.core.config import settings


class SkillExtractor:
    """Extracts and normalizes skills from job descriptions using NLP + gazetteer."""

    # Canonical skill gazetteer with synonyms
    SKILL_GAZETTEER: Dict[str, List[str]] = {
        "Python": ["python", "py"],
        "JavaScript": ["javascript", "js", "ecmascript"],
        "TypeScript": ["typescript", "ts"],
        "Java": ["java"],
        "C++": ["c++", "cpp"],
        "C#": ["c#", "csharp"],
        "Go": ["golang", "go"],
        "Rust": ["rust"],
        "Swift": ["swift"],
        "Kotlin": ["kotlin"],
        "PHP": ["php"],
        "Ruby": ["ruby"],
        "SQL": ["sql", "structured query language"],
        "NoSQL": ["nosql", "no sql"],
        "PostgreSQL": ["postgresql", "postgres"],
        "MySQL": ["mysql"],
        "MongoDB": ["mongodb", "mongo"],
        "Redis": ["redis"],
        "Elasticsearch": ["elasticsearch", "elastic"],
        "HTML": ["html", "html5"],
        "CSS": ["css", "css3"],
        "React": ["react", "reactjs", "react.js"],
        "Angular": ["angular", "angularjs"],
        "Vue": ["vue", "vuejs", "vue.js"],
        "Node.js": ["node", "nodejs", "node.js"],
        "Django": ["django"],
        "Flask": ["flask"],
        "FastAPI": ["fastapi"],
        "Spring Boot": ["spring boot", "springboot"],
        "Express": ["express", "expressjs"],
        "AWS": ["aws", "amazon web services"],
        "Azure": ["azure", "microsoft azure"],
        "GCP": ["gcp", "google cloud", "google cloud platform"],
        "Docker": ["docker"],
        "Kubernetes": ["kubernetes", "k8s"],
        "Terraform": ["terraform"],
        "Git": ["git", "github", "gitlab"],
        "CI/CD": ["ci/cd", "cicd", "continuous integration", "continuous deployment"],
        "Jenkins": ["jenkins"],
        "GitHub Actions": ["github actions"],
        "Linux": ["linux"],
        "Unix": ["unix"],
        "Machine Learning": ["machine learning", "ml"],
        "Deep Learning": ["deep learning", "dl"],
        "NLP": ["nlp", "natural language processing"],
        "Computer Vision": ["computer vision", "cv"],
        "TensorFlow": ["tensorflow", "tf"],
        "PyTorch": ["pytorch", "torch"],
        "Pandas": ["pandas"],
        "NumPy": ["numpy", "np"],
        "Scikit-learn": ["scikit-learn", "sklearn"],
        "Tableau": ["tableau"],
        "Power BI": ["power bi", "powerbi"],
        "Excel": ["excel", "microsoft excel"],
        "Statistics": ["statistics", "stat"],
        "Data Analysis": ["data analysis", "data analytics"],
        "Data Engineering": ["data engineering"],
        "ETL": ["etl"],
        "API": ["api", "rest api", "restful"],
        "GraphQL": ["graphql"],
        "Microservices": ["microservices", "micro services"],
        "REST": ["rest", "restful"],
        "Agile": ["agile", "scrum"],
        "Scrum": ["scrum"],
        "Project Management": ["project management", "pmp"],
        "Communication": ["communication", "communications"],
        "Leadership": ["leadership"],
        "Problem Solving": ["problem solving", "problem-solving"],
        "Teamwork": ["teamwork", "team work", "collaboration"],
        "Critical Thinking": ["critical thinking"],
        "Time Management": ["time management"],
        "PySpark": ["pyspark", "spark"],
        "Hadoop": ["hadoop"],
        "Kafka": ["kafka"],
        "Looker": ["looker"],
        "Snowflake": ["snowflake"],
        "Databricks": ["databricks"],
        "Airflow": ["airflow"],
        "Figma": ["figma"],
        "Adobe XD": ["adobe xd"],
        "Sketch": ["sketch"],
        "UI/UX": ["ui/ux", "ux/ui", "user experience", "user interface"],
        "Cybersecurity": ["cybersecurity", "cyber security", "security"],
        "Penetration Testing": ["penetration testing", "pentesting"],
        "DevOps": ["devops"],
        "Selenium": ["selenium"],
        "Cypress": ["cypress"],
        "Jest": ["jest"],
        "PyTest": ["pytest", "py.test"],
    }

    def __init__(self):
        self.nlp = self._load_spacy()
        self._stopwords = set()
        self._ensure_nltk()
        self._canonical_list = list(self.SKILL_GAZETTEER.keys())
        self._synonym_flat = []
        self._synonym_to_canonical = {}
        for canonical, synonyms in self.SKILL_GAZETTEER.items():
            for syn in [canonical.lower()] + [s.lower() for s in synonyms]:
                self._synonym_flat.append(syn)
                self._synonym_to_canonical[syn] = canonical

    def _ensure_nltk(self):
        for resource in ["punkt", "stopwords"]:
            try:
                nltk.data.find(f"tokenizers/{resource}" if resource == "punkt" else f"corpora/{resource}")
            except LookupError:
                nltk.download(resource, quiet=True)
        try:
            self._stopwords = set(stopwords.words("english"))
        except Exception:
            self._stopwords = set()

    def _load_spacy(self):
        try:
            return spacy.load(settings.spacy_model)
        except Exception:
            try:
                spacy.cli.download(settings.spacy_model)
                return spacy.load(settings.spacy_model)
            except Exception:
                return None

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"http\S+|www\.\S+", " ", text)
        text = re.sub(r"[^a-zA-Z0-9\s\+\#\.]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def normalize_skill(self, skill: str) -> Optional[str]:
        skill_lower = skill.strip().lower()
        if skill_lower in self._synonym_to_canonical:
            return self._synonym_to_canonical[skill_lower]
        match, score = process.extractOne(skill_lower, self._synonym_flat, scorer=fuzz.WRatio)
        if score >= 85:
            return self._synonym_to_canonical.get(match)
        return None

    def extract(self, text: str, min_confidence: float = 0.5) -> List[Dict]:
        """Return list of {skill, canonical, confidence, source}."""
        if not text:
            return []
        cleaned = self.clean_text(text)
        found: Dict[str, Dict] = {}

        # spaCy NER (organizations, products, etc.)
        if self.nlp:
            doc = self.nlp(cleaned)
            for ent in doc.ents:
                if ent.label_ in ("ORG", "PRODUCT", "SKILL", "WORK_OF_ART"):
                    canon = self.normalize_skill(ent.text)
                    if canon:
                        found[canon] = {
                            "skill": ent.text,
                            "canonical": canon,
                            "confidence": 0.8,
                            "source": "ner",
                        }

        # Gazetteer / keyword matching
        text_lower = cleaned.lower()
        for canonical, synonyms in self.SKILL_GAZETTEER.items():
            for syn in [canonical.lower()] + [s.lower() for s in synonyms]:
                if re.search(r"\b" + re.escape(syn) + r"\b", text_lower):
                    found[canonical] = {
                        "skill": syn,
                        "canonical": canonical,
                        "confidence": 0.9,
                        "source": "gazetteer",
                    }
                    break

        # Fuzzy fallback on tokens
        tokens = word_tokenize(cleaned)
        for token in tokens:
            if len(token) < 3 or token.lower() in self._stopwords:
                continue
            canon = self.normalize_skill(token)
            if canon and canon not in found:
                found[canon] = {
                    "skill": token,
                    "canonical": canon,
                    "confidence": 0.6,
                    "source": "fuzzy",
                }

        results = []
        for entry in found.values():
            if entry["confidence"] >= min_confidence:
                results.append(entry)
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results

    def extract_canonical_names(self, text: str) -> List[str]:
        return [e["canonical"] for e in self.extract(text)]

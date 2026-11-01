from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI-Based Job Market Skill Trend Analyzer"
    app_version: str = "1.0.0"
    debug: bool = True

    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = "sqlite:///./skill_trend.db"

    secret_key: str = "change-me-in-production-super-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    spacy_model: str = "en_core_web_sm"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @property
    def cors_origins_list(self) -> List[str]:
        return [x.strip() for x in self.backend_cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

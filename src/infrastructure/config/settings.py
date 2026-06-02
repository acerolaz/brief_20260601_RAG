"""Application settings — loaded from environment variables / .env file."""
from __future__ import annotations

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_env: str = "development"
    debug: bool = False
    project_name: str = "Tech Watch RAG Agent"
    api_v1_str: str = "/api/v1"
    log_level: str = "INFO"

    # Database / pgvector
    postgres_server: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: SecretStr = SecretStr("postgres")
    postgres_db: str = "tech_watch_rag"

    @property
    def database_url(self) -> str:
        pwd = self.postgres_password.get_secret_value()
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{pwd}"
            f"@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        )

    # LLM / Embeddings
    openai_api_key: SecretStr = SecretStr("")
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o"

    # LangSmith
    langchain_tracing_v2: bool = False
    langsmith_api_key: SecretStr = SecretStr("")
    langsmith_project: str = "tech_watch_rag"

    # Scraper
    scraper_timeout_seconds: int = 15


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings (singleton)."""
    return Settings()


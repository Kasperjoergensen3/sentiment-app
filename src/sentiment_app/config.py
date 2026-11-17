from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration comes from environment variables (or a local .env file)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    database_url: str = "sqlite:///./local.db"
    classifier_path: Path = Path("models/sentiment.joblib")

    @property
    def sqlalchemy_url(self) -> str:
        # Hosted Postgres gives "postgres://" or "postgresql://"; tell SQLAlchemy to use psycopg 3.
        for prefix in ("postgres://", "postgresql://"):
            if self.database_url.startswith(prefix):
                return "postgresql+psycopg://" + self.database_url.removeprefix(prefix)
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
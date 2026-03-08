from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    app_name: str = "myblog"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/myblog"
    secret_key: str = "change-me"

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")


settings = Settings()

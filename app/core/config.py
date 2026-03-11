from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_SQLITE_PATH = PROJECT_ROOT / "myblog.db"
DEFAULT_SQLITE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"


class Settings(BaseSettings):
    app_name: str = "myblog"
    database_url: str = DEFAULT_SQLITE_URL
    secret_key: str = "change-me"
    extension_modules: str = ""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")


settings = Settings()

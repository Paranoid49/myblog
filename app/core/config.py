from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_SQLITE_PATH = PROJECT_ROOT / "myblog.db"
DEFAULT_SQLITE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"


class Settings(BaseSettings):
    app_name: str = "myblog"
    database_url: str = DEFAULT_SQLITE_URL
    secret_key: str = "change-me"
    # 运行环境：development 或 production
    environment: str = "development"
    extension_modules: str = ""
    # 数据库连接池大小（仅对 PostgreSQL 生效，SQLite 忽略）
    db_pool_size: int = 5

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        supported = ("sqlite:///", "postgresql://", "postgresql+psycopg://", "postgresql+psycopg2://")
        if not v.startswith(supported):
            raise ValueError(f"不支持的数据库 URL 格式: {v}")
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key_length(cls, v: str) -> str:
        if v != "change-me" and len(v) < 32:
            raise ValueError("SECRET_KEY 长度应不少于 32 个字符")
        return v

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")


settings = Settings()

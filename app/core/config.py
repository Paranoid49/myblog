from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "myblog"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/myblog"
    secret_key: str = "change-me"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

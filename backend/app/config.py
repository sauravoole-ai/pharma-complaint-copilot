from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/complaints"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    frontend_origin: str = "http://localhost:5173"
    max_upload_bytes: int = Field(default=5 * 1024 * 1024, gt=0)


@lru_cache
def get_settings() -> Settings:
    return Settings()

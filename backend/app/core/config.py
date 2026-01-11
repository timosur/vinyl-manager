from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, PostgresDsn, validator
from pydantic.networks import AnyHttpUrl


class Settings(BaseSettings):
  PROJECT_NAME: str = "Vinyl Manager"

  API_PATH: str = "/api/v1"

  ACCESS_TOKEN_EXPIRE_MINUTES: int = 7 * 24 * 60  # 7 days

  DISCOGS_USER_TOKEN: str

  BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
    "http://localhost:8000",
    "http://localhost:3000",
    "https://vinyl.docker.local",
    "https://vinyl.home.timosur.com",
  ]

  # The following variables need to be defined in environment
  DATABASE_URL: PostgresDsn
  ASYNC_DATABASE_URL: Optional[PostgresDsn]

  @validator("ASYNC_DATABASE_URL", pre=True, always=True)
  def build_async_database_url(cls, v: Optional[str], values: Dict[str, Any]):
    """Builds ASYNC_DATABASE_URL from DATABASE_URL."""
    if v:
      return v
    database_url = values.get("DATABASE_URL")
    if database_url:
      # Replace postgresql:// with postgresql+asyncpg://
      return database_url.replace("postgresql", "postgresql+asyncpg", 1)
    return v

  class Config:
    case_sensitive = True


settings = Settings()

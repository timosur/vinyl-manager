from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, PostgresDsn, validator
from pydantic.networks import AnyHttpUrl

class Settings(BaseSettings):
    PROJECT_NAME: str = "Vinyl Manager"

    API_PATH: str = "/api/v1"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 7 * 24 * 60  # 7 days

    DISCOGS_USER_TOKEN: str

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ['http://localhost:8000','http://localhost:3000','https://vinyl.docker.local']

    # The following variables need to be defined in environment
    DATABASE_URL: PostgresDsn
    CLEAN_DATABASE_URL: Optional[PostgresDsn]
    ASYNC_DATABASE_URL: Optional[PostgresDsn]
    
    @validator("CLEAN_DATABASE_URL")
    def build_clean_database_url(cls, v: Optional[str], values: Dict[str, Any]):
        """Builds CLEAN_DATABASE_URL from DATABASE_URL."""
        v = values["DATABASE_URL"]
        # Replace vinyl-postgres.vinyl-manager with vinyl-postgres.vinyl-manager.svc.cluster.local
        return v.replace("vinyl-postgres.vinyl-manager", "vinyl-postgres.vinyl-manager.svc.cluster.local", 1) if v else v

    @validator("ASYNC_DATABASE_URL")
    def build_async_database_url(cls, v: Optional[str], values: Dict[str, Any]):
        """Builds ASYNC_DATABASE_URL from DATABASE_URL."""
        v = values["DATABASE_URL"]
        # Replace vinyl-postgres.vinyl-manager with vinyl-postgres-async.vinyl-manager.svc.cluster.local
        v = v.replace("vinyl-postgres.vinyl-manager", "vinyl-postgres-async.vinyl-manager.svc.cluster.local", 1) if v else v
        # Replace postgresql:// with postgresql+asyncpg://
        return v.replace("postgresql", "postgresql+asyncpg", 1) if v else v


settings = Settings()

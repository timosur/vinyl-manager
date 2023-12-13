import sys
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, HttpUrl, PostgresDsn, validator
from pydantic.networks import AnyHttpUrl


class Settings(BaseSettings):
    PROJECT_NAME: str = "Timesheet Automation"

    SENTRY_DSN: Optional[HttpUrl] = None

    API_PATH: str = "/api/v1"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 7 * 24 * 60  # 7 days

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ['http://localhost:8000','http://localhost:3000','https://vinyl.docker.local']

    # The following variables need to be defined in environment

    TEST_DATABASE_URL: Optional[PostgresDsn]
    DATABASE_URL: PostgresDsn
    ASYNC_DATABASE_URL: Optional[PostgresDsn]

    @validator("DATABASE_URL", pre=True)
    def build_test_database_url(cls, v: Optional[str], values: Dict[str, Any]):
        """Overrides DATABASE_URL with TEST_DATABASE_URL in test environment."""
        url = v
        if "pytest" in sys.modules:
            if not values.get("TEST_DATABASE_URL"):
                raise Exception(
                    "pytest detected, but TEST_DATABASE_URL is not set in environment"
                )
            url = values["TEST_DATABASE_URL"]
        if url:
            return url.replace("postgres://", "postgresql://")
        return url

    @validator("ASYNC_DATABASE_URL")
    def build_async_database_url(cls, v: Optional[str], values: Dict[str, Any]):
        """Builds ASYNC_DATABASE_URL from DATABASE_URL."""
        database_url = values["DATABASE_URL"]
        if database_url:
            # Replace 'postgresql' with 'postgresql+asyncpg'
            database_url = database_url.replace("postgresql", "postgresql+asyncpg", 1)
            # Remove '?sslmode=require' if present
            database_url = database_url.replace("?sslmode=require", "", 1)
        return database_url

    # @TodO: Change this to a real secret key and inject via env var
    SECRET_KEY: str = "yuTaK53Ze6vnKwFZY4SntZwH7"

    ## Emails

    SMTP_TLS: bool = False
    SMTP_PORT: Optional[int] = 25
    SMTP_HOST: Optional[str] = "10.99.128.52"
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = "timesheet-automation@rwe.com"
    EMAILS_FROM_NAME: Optional[str] = "Timesheet Automation"

    @validator("SMTP_HOST", pre=True, always=True)
    def set_smtp_host(cls, value, values):
            # Use value from environment variable if available, otherwise use the default value
            return values.get("SMTP_HOST", value)

    @validator("SMTP_PORT", pre=True, always=True)
    def set_smtp_port(cls, value, values):
            # Use value from environment variable if available, otherwise use the default value
            return values.get("SMTP_PORT", value)

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = True


settings = Settings()

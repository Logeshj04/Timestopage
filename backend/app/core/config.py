from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "testing", "production"] = "development"
    app_name: str = "Production Downtime Management System"
    company_name: str = "Your Company"
    timezone: str = "Asia/Kolkata"

    secret_key: str = Field(default="dev-secret-key-change-in-production")
    jwt_secret: str = Field(default="dev-jwt-secret-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    database_url: str = "postgresql+asyncpg://pdms:pdms@localhost:5432/pdms"

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    dev_admin_username: str = "admin"
    dev_admin_password: str = "ChangeMeAdmin123!"
    dev_supervisor_username: str = "supervisor"
    dev_supervisor_password: str = "ChangeMeSupervisor123!"
    seed_demo_stoppages: bool = False

    login_max_attempts: int = 8
    login_lockout_seconds: int = 300
    report_max_rows: int = 50000

    @field_validator("cors_origins")
    @classmethod
    def strip_origins(cls, value: str) -> str:
        return value.strip()

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")


@lru_cache
def get_settings() -> Settings:
    return Settings()

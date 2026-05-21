"""Core application configuration."""
from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "SecureExam Pro"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # API
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Database - Handle Render.com PostgreSQL
    database_url: str = "postgresql://postgres:postgres@localhost:5432/secureexam"
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Security
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]

    # AI/ML
    ai_model_path: str = "/models"
    face_detection_confidence: float = 0.7
    gaze_detection_threshold: float = 0.5
    max_faces_detected: int = 1
    suspicious_absence_frames: int = 30

    # Storage
    upload_dir: str = "/tmp/uploads"
    export_dir: str = "/tmp/exports"

    # Logging
    log_level: str = "INFO"

    @property
    def database_url_dsn(self) -> PostgresDsn:
        """Get database URL as PostgresDsn."""
        return PostgresDsn(self.database_url)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
"""Configuration management for Healthcare Care Coordinator Agent"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/healthcare_coordinator"
    sqlalchemy_echo: bool = False

    # Vector DB
    pgvector_enabled: bool = True
    milvus_host: str = "localhost"
    milvus_port: int = 19530

    # LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"

    # Security
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    log_level: str = "INFO"

    # PII Masking
    enable_pii_masking: bool = True
    pii_mask_strategy: str = "partial"  # partial, full, or hash

    # Audit
    audit_log_enabled: bool = True
    audit_log_retention_days: int = 365

    # Policy
    policy_validation_enabled: bool = True
    strict_mode: bool = False

    # Approval Workflow
    approval_timeout_minutes: int = 60
    require_human_approval_for_care_plans: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

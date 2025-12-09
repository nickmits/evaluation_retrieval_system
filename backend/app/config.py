"""
Configuration management for the RAG Evaluation Backend API
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    API_TITLE: str = "RAG Evaluation API"
    API_VERSION: str = "0.1.0"
    API_DESCRIPTION: str = "REST API for RAG retrieval system evaluation"
    API_PREFIX: str = "/api/v1"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    RELOAD: bool = True

    # CORS Configuration
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]

    # API Keys (Required)
    OPENAI_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None

    # File Upload Configuration
    UPLOAD_DIR: str = "temp_uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100 MB
    ALLOWED_FILE_TYPES: list[str] = ["pdf", "txt", "docx"]

    # Evaluation Configuration
    DEFAULT_NUM_QUESTIONS: int = 5
    MAX_NUM_QUESTIONS: int = 20
    MIN_NUM_QUESTIONS: int = 3

    # Task Management
    TASK_TIMEOUT: int = 3600  # 1 hour in seconds

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance

    Returns:
        Settings: Application settings
    """
    return Settings()

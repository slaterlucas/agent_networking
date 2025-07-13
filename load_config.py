"""Configuration loader using pydantic-settings to load from .env file."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration loaded from environment variables and .env file."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Exa API configuration
    exa_api_key: str = Field(description="API key for Exa search service")
    
    # Google Cloud configuration
    google_cloud_project: str = Field(description="Google Cloud project ID")
    google_cloud_location: str = Field(default="us-central1", description="Google Cloud region")
    google_genai_use_vertexai: bool = Field(default=True, description="Whether to use Vertex AI for GenAI")
    google_api_key: str = Field(description="Google API key")


def load_config() -> Config:
    """Load configuration from environment variables and .env file.
    
    Returns:
        Config: Validated configuration object
        
    Raises:
        ValidationError: If required configuration is missing or invalid
    """
    return Config()


# Global config instance for easy importing
config = load_config()
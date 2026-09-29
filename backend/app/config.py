"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API
    app_name: str = "OrchestrAI"
    api_prefix: str = "/api"
    cors_origins: str = "http://localhost:3000"

    # Database
    database_url: str = "sqlite:///./orchestr_ai.db"

    # LLM
    anthropic_api_key: str = ""
    anthropic_base_url: str = ""  # e.g. "https://your-gateway.example.com" — leave blank for api.anthropic.com
    anthropic_model: str = "claude-sonnet-4-20250514"
    planner_max_retries: int = 3
    planner_temperature: float = 0.0

    # Execution
    default_tool_timeout: int = 30
    max_retry_attempts: int = 3
    retry_backoff_base: float = 1.0

    # Approval
    approval_timeout_hours: int = 48

    class Config:
        env_file = ".env"


settings = Settings()

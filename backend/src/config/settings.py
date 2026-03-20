from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_env: str = "development"
    app_port: int = 8000
    cors_origins: str = "http://localhost:5173"

    mistral_api_key: str = ""
    database_url: str = "postgresql+asyncpg://entredeux:entredeux_dev@localhost:5432/entredeux"
    database_url_sync: str = "postgresql://entredeux:entredeux_dev@localhost:5432/entredeux"
    audit_enabled: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()

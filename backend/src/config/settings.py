from pydantic import model_validator
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

    demo_api_token: str = ""

    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    rate_limit_enabled: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @model_validator(mode="after")
    def validate_mistral_key(self) -> "Settings":
        """Fail fast if Mistral API key is missing in production."""
        if self.app_env == "production" and not self.mistral_api_key:
            raise ValueError(
                "MISTRAL_API_KEY is required in production. "
                "Set it in your .env file."
            )
        return self


settings = Settings()

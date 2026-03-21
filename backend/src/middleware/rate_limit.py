from fastapi import Request

from src.config.settings import settings


def get_rate_limit_key(request: Request) -> str:
    """Extract user ID from JWT for per-user rate limiting, fall back to IP."""
    if settings.jwt_secret_key:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ").strip()
            try:
                from src.services.auth_service import AuthService

                auth_svc = AuthService.__new__(AuthService)
                user_id = auth_svc.verify_access_token(token)
                return str(user_id)
            except (ValueError, Exception):
                pass
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = request.client
    return client.host if client else "unknown"


AI_RATE_LIMIT = "5/minute"
AUTH_RATE_LIMIT = "10/minute"

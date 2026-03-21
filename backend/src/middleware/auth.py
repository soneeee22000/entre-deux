from fastapi import Depends, HTTPException, Request

from src.config.settings import settings


async def verify_token(request: Request) -> None:
    """Verify Bearer token if configured, skip in dev with no token set."""
    if not settings.demo_api_token:
        return

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization token")

    token = auth_header.removeprefix("Bearer ").strip()
    if token != settings.demo_api_token:
        raise HTTPException(status_code=401, detail="Invalid authorization token")


require_auth = Depends(verify_token)

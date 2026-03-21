import uuid

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.db.engine import get_session
from src.db.repositories.user_repository import UserRepository
from src.db.tables import UserTable
from src.services.auth_service import AuthService


async def verify_token(request: Request) -> None:
    """Verify Bearer token if configured, skip in dev with no token set."""
    if not settings.demo_api_token and not settings.jwt_secret_key:
        return

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization token")

    token = auth_header.removeprefix("Bearer ").strip()

    if settings.jwt_secret_key:
        auth_svc = AuthService.__new__(AuthService)
        try:
            auth_svc.verify_access_token(token)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail="Invalid token") from exc
        return

    if settings.demo_api_token and token != settings.demo_api_token:
        raise HTTPException(status_code=401, detail="Invalid authorization token")


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> UserTable | None:
    """Extract authenticated user from JWT. Returns None if auth not configured."""
    if not settings.jwt_secret_key:
        return None

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization token")

    token = auth_header.removeprefix("Bearer ").strip()
    auth_svc = AuthService(session)

    try:
        user_id = auth_svc.verify_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    user = await UserRepository(session).get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Account deactivated")

    return user


async def get_current_patient_id(
    user: UserTable | None = Depends(get_current_user),  # noqa: B008
) -> uuid.UUID | None:
    """Extract current patient_id from authenticated user."""
    if user is None:
        return None
    return user.patient_id


def require_patient_match(
    path_patient_id: uuid.UUID,
    current_patient_id: uuid.UUID | None,
) -> None:
    """Verify path patient_id matches the authenticated user's patient_id."""
    if current_patient_id is None:
        return
    if path_patient_id != current_patient_id:
        raise HTTPException(
            status_code=403,
            detail="Acces interdit aux donnees d'un autre patient",
        )


require_auth = Depends(verify_token)

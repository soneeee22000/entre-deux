from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.engine import get_session
from src.models.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_auth_service(
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> AuthService:
    """Provide an AuthService instance."""
    return AuthService(session)


@router.post("/register", status_code=201, response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    service: AuthService = Depends(_get_auth_service),  # noqa: B008
) -> TokenResponse:
    """Register a new user account with patient and consent."""
    try:
        user, patient = await service.register(
            email=request.email,
            password=request.password,
            given_name=request.given_name,
            family_name=request.family_name,
            identifier=request.identifier,
        )
    except Exception as exc:
        detail = str(exc)
        if "unique" in detail.lower() or "duplicate" in detail.lower():
            raise HTTPException(
                status_code=409, detail="Email ou identifiant deja utilise"
            ) from exc
        raise HTTPException(status_code=400, detail=detail) from exc

    return TokenResponse(
        access_token=service.create_access_token(user.id),
        refresh_token=service.create_refresh_token(user.id),
        patient_id=str(patient.id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    service: AuthService = Depends(_get_auth_service),  # noqa: B008
) -> TokenResponse:
    """Authenticate and return a JWT token pair."""
    try:
        user = await service.authenticate(request.email, request.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Identifiants invalides") from exc

    return TokenResponse(
        access_token=service.create_access_token(user.id),
        refresh_token=service.create_refresh_token(user.id),
        patient_id=str(user.patient_id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
    service: AuthService = Depends(_get_auth_service),  # noqa: B008
) -> TokenResponse:
    """Exchange a refresh token for a new token pair."""
    try:
        user_id = service.verify_refresh_token(request.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=401, detail="Jeton de rafraichissement invalide"
        ) from exc

    from src.db.repositories.user_repository import UserRepository

    user = await UserRepository(service._session).get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Compte desactive")

    return TokenResponse(
        access_token=service.create_access_token(user.id),
        refresh_token=service.create_refresh_token(user.id),
        patient_id=str(user.patient_id),
    )

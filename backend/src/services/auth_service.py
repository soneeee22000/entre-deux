import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.db.repositories.consent_repository import ConsentRepository
from src.db.repositories.patient_repository import PatientRepository
from src.db.repositories.user_repository import UserRepository
from src.db.tables import ConsentTable, PatientTable, UserTable
from src.models.fhir_helpers import create_consent, create_patient

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Handles user registration, authentication, and JWT token management."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_repo = UserRepository(session)
        self._patient_repo = PatientRepository(session)
        self._consent_repo = ConsentRepository(session)

    async def register(
        self,
        email: str,
        password: str,
        given_name: str,
        family_name: str,
        identifier: str,
    ) -> tuple[UserTable, PatientTable]:
        """Register a new user with patient + consent atomically."""
        fhir_patient = create_patient(given_name, family_name, identifier)
        patient_row = PatientTable(
            identifier=identifier,
            fhir_resource=fhir_patient.model_dump(mode="json"),
        )
        created_patient = await self._patient_repo.create(patient_row)
        created_patient.fhir_resource["id"] = str(created_patient.id)

        user_row = UserTable(
            email=email.lower().strip(),
            password_hash=pwd_context.hash(password),
            patient_id=created_patient.id,
            is_active=True,
        )
        created_user = await self._user_repo.create(user_row)

        patient_ref = f"Patient/{created_patient.id}"
        fhir_consent = create_consent(patient_ref, "ai-processing")
        consent_row = ConsentTable(
            patient_id=created_patient.id,
            scope="ai-processing",
            active=True,
            fhir_resource=fhir_consent.model_dump(mode="json"),
        )
        await self._consent_repo.create(consent_row)

        await self._session.commit()
        return created_user, created_patient

    async def authenticate(self, email: str, password: str) -> UserTable:
        """Verify credentials and return user, or raise ValueError."""
        user = await self._user_repo.get_by_email(email.lower().strip())
        if not user or not pwd_context.verify(password, user.password_hash):
            raise ValueError("Invalid credentials")
        if not user.is_active:
            raise ValueError("Account is deactivated")
        return user

    def create_access_token(self, user_id: uuid.UUID) -> str:
        """Create a short-lived JWT access token."""
        expire = datetime.now(tz=timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "access",
        }
        return str(jwt.encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        ))

    def create_refresh_token(self, user_id: uuid.UUID) -> str:
        """Create a long-lived JWT refresh token."""
        expire = datetime.now(tz=timezone.utc) + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh",
        }
        return str(jwt.encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        ))

    def verify_access_token(self, token: str) -> uuid.UUID:
        """Decode an access token and return the user_id."""
        try:
            payload = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
        except JWTError as exc:
            raise ValueError("Invalid token") from exc

        if payload.get("type") != "access":
            raise ValueError("Invalid token type")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise ValueError("Missing subject in token")
        return uuid.UUID(user_id_str)

    def verify_refresh_token(self, token: str) -> uuid.UUID:
        """Decode a refresh token and return the user_id."""
        try:
            payload = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
            )
        except JWTError as exc:
            raise ValueError("Invalid refresh token") from exc

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise ValueError("Missing subject in token")
        return uuid.UUID(user_id_str)

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

TEST_JWT_SECRET = "test-jwt-signing-material"

from src.services.auth_service import AuthService, pwd_context


@pytest.fixture
def auth_service(mock_session: AsyncMock) -> AuthService:
    """Provide an AuthService instance with mock session."""
    return AuthService(mock_session)


class TestPasswordHashing:
    """Test bcrypt password hashing."""

    def test_hash_and_verify(self) -> None:
        """Hashed password should verify correctly."""
        hashed = pwd_context.hash("testpassword")
        assert pwd_context.verify("testpassword", hashed)

    def test_wrong_password_fails(self) -> None:
        """Wrong password should not verify."""
        hashed = pwd_context.hash("correctpassword")
        assert not pwd_context.verify("wrongpassword", hashed)


class TestTokens:
    """Test JWT token creation and verification."""

    @patch("src.services.auth_service.settings")
    def test_create_and_verify_access_token(
        self, mock_settings: MagicMock, auth_service: AuthService
    ) -> None:
        """Access token should roundtrip through create/verify."""
        mock_settings.jwt_secret_key = TEST_JWT_SECRET
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.jwt_access_token_expire_minutes = 15
        user_id = uuid.uuid4()

        token = auth_service.create_access_token(user_id)
        verified_id = auth_service.verify_access_token(token)

        assert verified_id == user_id

    @patch("src.services.auth_service.settings")
    def test_create_and_verify_refresh_token(
        self, mock_settings: MagicMock, auth_service: AuthService
    ) -> None:
        """Refresh token should roundtrip through create/verify."""
        mock_settings.jwt_secret_key = TEST_JWT_SECRET
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.jwt_refresh_token_expire_days = 7
        user_id = uuid.uuid4()

        token = auth_service.create_refresh_token(user_id)
        verified_id = auth_service.verify_refresh_token(token)

        assert verified_id == user_id

    @patch("src.services.auth_service.settings")
    def test_access_token_rejects_refresh(
        self, mock_settings: MagicMock, auth_service: AuthService
    ) -> None:
        """Access token verification should reject refresh tokens."""
        mock_settings.jwt_secret_key = TEST_JWT_SECRET
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.jwt_refresh_token_expire_days = 7
        user_id = uuid.uuid4()

        token = auth_service.create_refresh_token(user_id)

        with pytest.raises(ValueError, match="Invalid token type"):
            auth_service.verify_access_token(token)

    @patch("src.services.auth_service.settings")
    def test_invalid_token_raises(
        self, mock_settings: MagicMock, auth_service: AuthService
    ) -> None:
        """Garbage token should raise ValueError."""
        mock_settings.jwt_secret_key = TEST_JWT_SECRET
        mock_settings.jwt_algorithm = "HS256"

        with pytest.raises(ValueError, match="Invalid token"):
            auth_service.verify_access_token("garbage-token")


class TestAuthenticate:
    """Test user authentication."""

    @pytest.mark.asyncio
    async def test_invalid_email_raises(
        self, auth_service: AuthService
    ) -> None:
        """Non-existent email should raise ValueError."""
        with patch.object(
            auth_service, "_user_repo"
        ) as mock_repo:
            mock_repo.get_by_email = AsyncMock(return_value=None)

            with pytest.raises(ValueError, match="Invalid credentials"):
                await auth_service.authenticate("no@one.com", "password")

    @pytest.mark.asyncio
    async def test_wrong_password_raises(
        self, auth_service: AuthService
    ) -> None:
        """Correct email but wrong password should raise ValueError."""
        user_mock = MagicMock()
        user_mock.password_hash = pwd_context.hash("correct")
        user_mock.is_active = True

        with patch.object(
            auth_service, "_user_repo"
        ) as mock_repo:
            mock_repo.get_by_email = AsyncMock(return_value=user_mock)

            with pytest.raises(ValueError, match="Invalid credentials"):
                await auth_service.authenticate("user@test.com", "wrong")

    @pytest.mark.asyncio
    async def test_valid_credentials_returns_user(
        self, auth_service: AuthService
    ) -> None:
        """Correct credentials should return user."""
        user_mock = MagicMock()
        user_mock.password_hash = pwd_context.hash("correct")
        user_mock.is_active = True

        with patch.object(
            auth_service, "_user_repo"
        ) as mock_repo:
            mock_repo.get_by_email = AsyncMock(return_value=user_mock)

            result = await auth_service.authenticate("user@test.com", "correct")
            assert result == user_mock

    @pytest.mark.asyncio
    async def test_inactive_user_raises(
        self, auth_service: AuthService
    ) -> None:
        """Deactivated user should raise ValueError."""
        user_mock = MagicMock()
        user_mock.password_hash = pwd_context.hash("correct")
        user_mock.is_active = False

        with patch.object(
            auth_service, "_user_repo"
        ) as mock_repo:
            mock_repo.get_by_email = AsyncMock(return_value=user_mock)

            with pytest.raises(ValueError, match="deactivated"):
                await auth_service.authenticate("user@test.com", "correct")

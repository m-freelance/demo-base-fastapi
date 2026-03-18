"""
Tests for AuthService.

This module contains unit tests for authentication service operations.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.api.auth.auth_service import AuthService
from backend.api.auth.auth_dtos import (
    RegisterRequestDto,
    RegisterResponseDto,
    LoginRequestDto,
    LoginResponseDto,
)
from backend.api.auth.auth_exceptions import (
    UserExistsException,
    UserCreateInternalErrorException,
    InvalidCredentialsException,
)
from backend.api.auth.password_hasher import PasswordHasher
from backend.api.auth.token_service import TokenService
from backend.api.schemas.user import User, UserRole
from backend.api.user.user_repository import UserRepository


class TestAuthService:
    """Unit tests for AuthService."""

    @pytest.fixture
    def mock_user_repository(self) -> AsyncMock:
        """Create a mock UserRepository."""
        return AsyncMock(spec=UserRepository)

    @pytest.fixture
    def mock_password_hasher(self) -> MagicMock:
        """Create a mock PasswordHasher."""
        mock = MagicMock(spec=PasswordHasher)
        mock.encrypt_password.return_value = "hashed_password_123"
        mock.verify_password.return_value = True
        return mock

    @pytest.fixture
    def mock_db_session(self) -> AsyncMock:
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_token_service(self) -> MagicMock:
        """Create a mock TokenService."""
        mock = MagicMock(spec=TokenService)
        mock.create_access_token.return_value = "test_jwt_token_12345"
        return mock

    @pytest.fixture
    def auth_service(
        self,
        mock_user_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        mock_db_session: AsyncMock,
        mock_token_service: MagicMock,
    ) -> AuthService:
        """Create an AuthService instance for testing."""
        return AuthService(
            user_repository=mock_user_repository,
            password_hasher=mock_password_hasher,
            db_session=mock_db_session,
            token_service=mock_token_service,
        )

    @pytest.fixture
    def sample_register_request(self) -> RegisterRequestDto:
        """Create a sample registration request."""
        return RegisterRequestDto(
            email="newuser@example.com",
            password="securepassword123",
        )

    @pytest.fixture
    def sample_user(self) -> User:
        """Create a sample User entity."""
        return User(
            id=1,
            user_uuid="a400b358-71ca-4f15-9c9e-2193ebf9c06b",
            email="newuser@example.com",
            hashed_password="hashed_password_123",
            is_active=True,
            role=UserRole.USER,
        )

    ### add_new_user tests ###
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_new_user_success(
        self,
        auth_service: AuthService,
        mock_user_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        mock_db_session: AsyncMock,
        sample_register_request: RegisterRequestDto,
        sample_user: User,
    ):
        """Test successful user registration."""
        mock_user_repository.find_user_by_email.return_value = None
        mock_user_repository.add_new_user.return_value = sample_user

        result = await auth_service.add_new_user(user=sample_register_request)

        assert isinstance(result, RegisterResponseDto)
        assert result.email == sample_user.email
        mock_password_hasher.encrypt_password.assert_called_once_with(
            sample_register_request.password
        )
        mock_user_repository.find_user_by_email.assert_called_once()
        mock_user_repository.add_new_user.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_new_user_raises_exception_when_user_exists(
        self,
        auth_service: AuthService,
        mock_user_repository: AsyncMock,
        sample_register_request: RegisterRequestDto,
        sample_user: User,
    ):
        """Test that registration raises UserExistsException when user already exists."""
        mock_user_repository.find_user_by_email.return_value = sample_user

        with pytest.raises(UserExistsException) as exc_info:
            await auth_service.add_new_user(user=sample_register_request)

        assert sample_register_request.email in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_new_user_raises_internal_error_on_db_exception(
        self,
        auth_service: AuthService,
        mock_user_repository: AsyncMock,
        sample_register_request: RegisterRequestDto,
    ):
        """Test that registration raises UserCreateInternalErrorException on DB error."""
        mock_user_repository.find_user_by_email.return_value = None
        mock_user_repository.add_new_user.side_effect = Exception("Database error")

        with pytest.raises(UserCreateInternalErrorException):
            await auth_service.add_new_user(user=sample_register_request)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_new_user_encrypts_password(
        self,
        auth_service: AuthService,
        mock_user_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        sample_register_request: RegisterRequestDto,
        sample_user: User,
    ):
        """Test that password is encrypted before storing."""
        mock_user_repository.find_user_by_email.return_value = None
        mock_user_repository.add_new_user.return_value = sample_user

        await auth_service.add_new_user(user=sample_register_request)

        mock_password_hasher.encrypt_password.assert_called_once_with(
            sample_register_request.password
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_new_user_creates_user_with_user_role(
        self,
        auth_service: AuthService,
        mock_user_repository: AsyncMock,
        sample_register_request: RegisterRequestDto,
        sample_user: User,
    ):
        """Test that new user is created with USER role by default."""
        mock_user_repository.find_user_by_email.return_value = None
        mock_user_repository.add_new_user.return_value = sample_user

        await auth_service.add_new_user(user=sample_register_request)

        # Verify that add_new_user was called with a User object with USER role
        call_args = mock_user_repository.add_new_user.call_args
        user_arg = call_args[0][0]
        assert user_arg.role == UserRole.USER

    ### login tests ###
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_success(
        self,
        auth_service: AuthService,
        mock_user_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        mock_token_service: MagicMock,
        sample_user: User,
    ):
        """Test successful login."""
        mock_user_repository.find_user_by_email.return_value = sample_user
        mock_password_hasher.verify_password.return_value = True

        login_request = LoginRequestDto(
            username="newuser@example.com",
            password="securepassword123",
        )

        result = await auth_service.login(login_request=login_request)

        assert isinstance(result, LoginResponseDto)
        assert result.access_token == "test_jwt_token_12345"
        assert result.token_type == "bearer"
        mock_token_service.create_access_token.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_raises_exception_for_nonexistent_user(
        self,
        auth_service: AuthService,
        mock_user_repository: AsyncMock,
    ):
        """Test that login raises InvalidCredentialsException for non-existent user."""
        mock_user_repository.find_user_by_email.return_value = None

        login_request = LoginRequestDto(
            username="nonexistent@example.com",
            password="securepassword123",
        )

        with pytest.raises(InvalidCredentialsException):
            await auth_service.login(login_request=login_request)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_raises_exception_for_wrong_password(
        self,
        auth_service: AuthService,
        mock_user_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        sample_user: User,
    ):
        """Test that login raises InvalidCredentialsException for wrong password."""
        mock_user_repository.find_user_by_email.return_value = sample_user
        mock_password_hasher.verify_password.return_value = False

        login_request = LoginRequestDto(
            username="newuser@example.com",
            password="wrongpassword",
        )

        with pytest.raises(InvalidCredentialsException):
            await auth_service.login(login_request=login_request)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_verifies_password(
        self,
        auth_service: AuthService,
        mock_user_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        sample_user: User,
    ):
        """Test that login verifies the password."""
        mock_user_repository.find_user_by_email.return_value = sample_user
        mock_password_hasher.verify_password.return_value = True

        login_request = LoginRequestDto(
            username="newuser@example.com",
            password="securepassword123",
        )

        await auth_service.login(login_request=login_request)

        mock_password_hasher.verify_password.assert_called_once_with(
            "securepassword123", sample_user.hashed_password
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_creates_token_with_correct_data(
        self,
        auth_service: AuthService,
        mock_user_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        mock_token_service: MagicMock,
        sample_user: User,
    ):
        """Test that login creates token with correct user data."""
        mock_user_repository.find_user_by_email.return_value = sample_user
        mock_password_hasher.verify_password.return_value = True

        login_request = LoginRequestDto(
            username="newuser@example.com",
            password="securepassword123",
        )

        await auth_service.login(login_request=login_request)

        call_args = mock_token_service.create_access_token.call_args
        token_data = call_args.kwargs.get("data") or call_args[1].get("data")
        assert token_data.email == sample_user.email
        assert token_data.role == sample_user.role

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_returns_bearer_token_type(
        self,
        auth_service: AuthService,
        mock_user_repository: AsyncMock,
        mock_password_hasher: MagicMock,
        sample_user: User,
    ):
        """Test that login returns 'bearer' as token type."""
        mock_user_repository.find_user_by_email.return_value = sample_user
        mock_password_hasher.verify_password.return_value = True

        login_request = LoginRequestDto(
            username="newuser@example.com",
            password="securepassword123",
        )

        result = await auth_service.login(login_request=login_request)

        assert result.token_type == "bearer"

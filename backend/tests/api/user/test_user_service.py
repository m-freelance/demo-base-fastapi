"""
Tests for UserService.

This module contains unit tests for user service operations.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi_pagination import Page

from backend.api.schemas.user import User, UserRole
from backend.api.user.user_repository import UserRepository
from backend.api.user.user_service import UserService


class TestUserService:
    """Unit tests for UserService."""

    @pytest.fixture
    def mock_user_repository(self) -> AsyncMock:
        """Create a mock UserRepository."""
        return AsyncMock(spec=UserRepository)

    @pytest.fixture
    def mock_db_session(self) -> AsyncMock:
        """Create a mock database session."""
        return AsyncMock()

    @pytest.fixture
    def user_service(
        self,
        mock_user_repository: AsyncMock,
        mock_db_session: AsyncMock,
    ) -> UserService:
        """Create a UserService instance for testing."""
        return UserService(
            user_repository=mock_user_repository,
            db_session=mock_db_session,
        )

    @pytest.fixture
    def sample_user(self) -> User:
        """Create a sample User entity."""
        return User(
            id=1,
            user_uuid="a400b358-71ca-4f15-9c9e-2193ebf9c06b",
            email="testuser@example.com",
            hashed_password="hashed_password_123",
            is_active=True,
            role=UserRole.USER,
        )

    @pytest.fixture
    def admin_user(self) -> User:
        """Create an admin User entity."""
        return User(
            id=2,
            user_uuid="b500c459-82db-4a16-8d0f-3204fc00d17c",
            email="admin@example.com",
            hashed_password="hashed_password_456",
            is_active=True,
            role=UserRole.ADMIN,
        )

    @pytest.fixture
    def mock_users_page(self, sample_user: User, admin_user: User) -> Page[User]:
        """Create a mock paginated users response."""
        return Page(
            items=[sample_user, admin_user],
            total=2,
            page=1,
            size=50,
            pages=1,
        )

    @pytest.fixture
    def mock_empty_page(self) -> Page[User]:
        """Create a mock empty paginated response."""
        return Page(
            items=[],
            total=0,
            page=1,
            size=50,
            pages=0,
        )

    @pytest.fixture
    def mock_page_params(self) -> MagicMock:
        """Create mock pagination parameters."""
        return MagicMock()

    ### get_all_users tests ###
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_users_returns_page(
        self,
        user_service: UserService,
        mock_user_repository: AsyncMock,
        mock_users_page: Page[User],
        mock_page_params: MagicMock,
    ):
        """Test that get_all_users returns a paginated response."""
        mock_user_repository.get_all_users.return_value = mock_users_page

        result = await user_service.get_all_users(page_params=mock_page_params)

        assert isinstance(result, Page)
        assert result.total == 2
        assert len(result.items) == 2
        mock_user_repository.get_all_users.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_users_returns_empty_page_when_no_users(
        self,
        user_service: UserService,
        mock_user_repository: AsyncMock,
        mock_empty_page: Page[User],
        mock_page_params: MagicMock,
    ):
        """Test that get_all_users returns empty page when no users exist."""
        mock_user_repository.get_all_users.return_value = mock_empty_page

        result = await user_service.get_all_users(page_params=mock_page_params)

        assert result.total == 0
        assert len(result.items) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_users_passes_session_to_repository(
        self,
        user_service: UserService,
        mock_user_repository: AsyncMock,
        mock_db_session: AsyncMock,
        mock_users_page: Page[User],
        mock_page_params: MagicMock,
    ):
        """Test that get_all_users passes the db session to repository."""
        mock_user_repository.get_all_users.return_value = mock_users_page

        await user_service.get_all_users(page_params=mock_page_params)

        call_args = mock_user_repository.get_all_users.call_args
        assert call_args[0][0] == mock_db_session

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_users_passes_page_params_to_repository(
        self,
        user_service: UserService,
        mock_user_repository: AsyncMock,
        mock_users_page: Page[User],
        mock_page_params: MagicMock,
    ):
        """Test that get_all_users passes page params to repository."""
        mock_user_repository.get_all_users.return_value = mock_users_page

        await user_service.get_all_users(page_params=mock_page_params)

        call_args = mock_user_repository.get_all_users.call_args
        assert call_args[0][1] == mock_page_params

    ### get_user_by_email tests ###
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_user_by_email_returns_user_when_found(
        self,
        user_service: UserService,
        mock_user_repository: AsyncMock,
        sample_user: User,
    ):
        """Test that get_user_by_email returns user when found."""
        mock_user_repository.find_user_by_email.return_value = sample_user

        result = await user_service.get_user_by_email(email="testuser@example.com")

        assert result is not None
        assert result.email == "testuser@example.com"
        mock_user_repository.find_user_by_email.assert_called_once_with(
            "testuser@example.com", user_service._db_session
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_user_by_email_returns_none_when_not_found(
        self,
        user_service: UserService,
        mock_user_repository: AsyncMock,
    ):
        """Test that get_user_by_email returns None when user not found."""
        mock_user_repository.find_user_by_email.return_value = None

        result = await user_service.get_user_by_email(email="nonexistent@example.com")

        assert result is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_user_by_email_returns_admin_user(
        self,
        user_service: UserService,
        mock_user_repository: AsyncMock,
        admin_user: User,
    ):
        """Test that get_user_by_email returns admin user correctly."""
        mock_user_repository.find_user_by_email.return_value = admin_user

        result = await user_service.get_user_by_email(email="admin@example.com")

        assert result is not None
        assert result.role == UserRole.ADMIN

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_user_by_email_passes_session_to_repository(
        self,
        user_service: UserService,
        mock_user_repository: AsyncMock,
        mock_db_session: AsyncMock,
        sample_user: User,
    ):
        """Test that get_user_by_email passes the db session to repository."""
        mock_user_repository.find_user_by_email.return_value = sample_user

        await user_service.get_user_by_email(email="testuser@example.com")

        mock_user_repository.find_user_by_email.assert_called_once_with(
            "testuser@example.com", mock_db_session
        )

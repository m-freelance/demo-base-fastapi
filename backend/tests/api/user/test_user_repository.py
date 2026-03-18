"""
Tests for UserRepository.

This module contains:
- Unit tests: Fast tests using mocked database sessions
- Release tests: Integration tests using a real (in-memory SQLite) database
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.api.user.user_repository import UserRepository
from backend.api.schemas.user import User, UserRole


class TestUserRepositoryUnit:
    """Unit tests for UserRepository using mocked dependencies."""

    @pytest.fixture
    def repository(self) -> UserRepository:
        """Create a UserRepository instance for testing."""
        return UserRepository()

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Create a mocked AsyncSession."""
        session = AsyncMock()
        # session.add() is a synchronous method, so use MagicMock for it
        session.add = MagicMock()
        return session

    @pytest.fixture
    def sample_user(self) -> User:
        """Create a sample user for testing."""
        return User(
            id=1,
            email="test@example.com",
            hashed_password="hashed_password_123",
            is_active=True,
            user_uuid="test-uuid-1234",
            role=UserRole.USER,
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_new_user_adds_to_session(
        self, repository: UserRepository, mock_session: AsyncMock, sample_user: User
    ):
        """Test that add_new_user adds the user to the session."""
        # Act
        result = await repository.add_new_user(sample_user, mock_session)

        # Assert
        mock_session.add.assert_called_once_with(sample_user)
        assert result == sample_user

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_find_user_by_email_returns_user_when_found(
        self, repository: UserRepository, mock_session: AsyncMock, sample_user: User
    ):
        """Test that find_user_by_email returns user when found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.find_user_by_email("test@example.com", mock_session)

        # Assert
        assert result == sample_user
        mock_session.execute.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_find_user_by_email_returns_none_when_not_found(
        self, repository: UserRepository, mock_session: AsyncMock
    ):
        """Test that find_user_by_email returns None when user not found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await repository.find_user_by_email(
            "nonexistent@example.com", mock_session
        )

        # Assert
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_users_calls_paginate(
        self, repository: UserRepository, mock_session: AsyncMock
    ):
        """Test that get_all_users calls the paginate function."""
        # Arrange
        mock_page_params = MagicMock()
        mock_page = MagicMock()

        with patch(
            "backend.api.user.user_repository.paginate",
            new_callable=AsyncMock,
            return_value=mock_page,
        ) as mock_paginate:
            # Act
            result = await repository.get_all_users(mock_session, mock_page_params)

            # Assert
            mock_paginate.assert_called_once()
            assert result == mock_page


@pytest.mark.release
class TestUserRepositoryRelease:
    """Release tests for UserRepository using a real database."""

    @pytest.fixture
    def repository(self) -> UserRepository:
        """Create a UserRepository instance for testing."""
        return UserRepository()

    def create_user(
        self,
        email: str = "test@example.com",
        hashed_password: str = "hashed_password_123",
        is_active: bool = True,
        role: UserRole = UserRole.USER,
    ) -> User:
        """Helper to create a user instance."""
        return User(
            email=email,
            hashed_password=hashed_password,
            is_active=is_active,
            role=role,
        )

    @pytest.mark.asyncio
    async def test_add_new_user_persists_to_database(
        self, repository: UserRepository, db_session
    ):
        """Test that add_new_user actually persists the user to the database."""
        # Arrange
        user = self.create_user(email="newuser@example.com")

        # Act
        result = await repository.add_new_user(user, db_session)
        await db_session.flush()

        # Assert
        assert result.id is not None
        assert result.email == "newuser@example.com"
        assert result.user_uuid is not None

    @pytest.mark.asyncio
    async def test_find_user_by_email_finds_existing_user(
        self, repository: UserRepository, db_session
    ):
        """Test that find_user_by_email finds an existing user in the database."""
        # Arrange
        user = self.create_user(email="findme@example.com")
        await repository.add_new_user(user, db_session)
        await db_session.flush()

        # Act
        found_user = await repository.find_user_by_email(
            "findme@example.com", db_session
        )

        # Assert
        assert found_user is not None
        assert found_user.email == "findme@example.com"
        assert found_user.id == user.id

    @pytest.mark.asyncio
    async def test_find_user_by_email_returns_none_for_nonexistent_user(
        self, repository: UserRepository, db_session
    ):
        """Test that find_user_by_email returns None for a nonexistent email."""
        # Act
        result = await repository.find_user_by_email(
            "doesnotexist@example.com", db_session
        )

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_add_multiple_users_creates_unique_records(
        self, repository: UserRepository, db_session
    ):
        """Test that multiple users can be added with unique emails."""
        # Arrange
        user1 = self.create_user(email="user1@example.com")
        user2 = self.create_user(email="user2@example.com")
        user3 = self.create_user(email="user3@example.com")

        # Act
        await repository.add_new_user(user1, db_session)
        await repository.add_new_user(user2, db_session)
        await repository.add_new_user(user3, db_session)
        await db_session.flush()

        # Assert
        found1 = await repository.find_user_by_email("user1@example.com", db_session)
        found2 = await repository.find_user_by_email("user2@example.com", db_session)
        found3 = await repository.find_user_by_email("user3@example.com", db_session)

        assert found1 is not None
        assert found2 is not None
        assert found3 is not None
        assert found1.id != found2.id != found3.id

    @pytest.mark.asyncio
    async def test_user_role_is_persisted_correctly(
        self, repository: UserRepository, db_session
    ):
        """Test that user roles are correctly persisted and retrieved."""
        # Arrange
        admin_user = self.create_user(email="admin@example.com", role=UserRole.ADMIN)
        regular_user = self.create_user(email="regular@example.com", role=UserRole.USER)

        # Act
        await repository.add_new_user(admin_user, db_session)
        await repository.add_new_user(regular_user, db_session)
        await db_session.flush()

        # Assert
        found_admin = await repository.find_user_by_email(
            "admin@example.com", db_session
        )
        found_regular = await repository.find_user_by_email(
            "regular@example.com", db_session
        )

        assert found_admin is not None
        assert found_regular is not None
        assert found_admin.role == UserRole.ADMIN
        assert found_regular.role == UserRole.USER

    @pytest.mark.asyncio
    async def test_user_uuid_is_auto_generated(
        self, repository: UserRepository, db_session
    ):
        """Test that user_uuid is automatically generated when not provided."""
        # Arrange
        user = self.create_user(email="autouuid@example.com")

        # Act
        result = await repository.add_new_user(user, db_session)
        await db_session.flush()

        # Assert
        assert result.user_uuid is not None
        assert len(result.user_uuid) > 0

    @pytest.mark.asyncio
    async def test_is_active_defaults_to_true(
        self, repository: UserRepository, db_session
    ):
        """Test that is_active defaults to True for new users."""
        # Arrange
        user = User(
            email="active@example.com",
            hashed_password="hashed_password",
            role=UserRole.USER,
        )

        # Act
        result = await repository.add_new_user(user, db_session)
        await db_session.flush()

        # Assert
        assert result.is_active is True

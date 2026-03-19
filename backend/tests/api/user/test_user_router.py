"""
Unit tests for the user router endpoints.
Tests cover both the GET /users/me and GET /users endpoints, including successful cases,
validation errors, and expected exceptions.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_pagination import Page, add_pagination

from backend.api.auth.token_service import oauth2_scheme
from backend.api.schemas.user import User, UserRole
from backend.api.user.user_dependencies import get_current_user_info, get_user_service
from backend.api.user.user_router import router


### FIXTURES ###
@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    add_pagination(app)
    return app


@pytest.fixture
def mock_user():
    """Create a mock user object."""
    user = MagicMock(spec=User)
    user.id = 1
    user.user_uuid = "a400b358-71ca-4f15-9c9e-2193ebf9c06b"
    user.email = "testuser@example.com"
    user.is_active = True
    user.role = UserRole.USER
    user.hashed_password = "hashed_password_123"
    return user


@pytest.fixture
def mock_admin_user():
    """Create a mock admin user object."""
    user = MagicMock(spec=User)
    user.id = 2
    user.user_uuid = "b500c459-82db-4a16-8d0f-3204fc00d17c"
    user.email = "admin@example.com"
    user.is_active = True
    user.role = UserRole.ADMIN
    user.hashed_password = "hashed_password_456"
    return user


@pytest.fixture
def mock_inactive_user():
    """Create a mock inactive user object."""
    user = MagicMock(spec=User)
    user.id = 3
    user.user_uuid = "c600d560-93ec-4a27-ae1a-4315adb1e28d"
    user.email = "inactive@example.com"
    user.is_active = False
    user.role = UserRole.USER
    user.hashed_password = "hashed_password_789"
    return user


@pytest.fixture
def mock_users_page(mock_user, mock_admin_user):
    """Create a mock paginated users response."""
    return Page(
        items=[mock_user, mock_admin_user],
        total=2,
        page=1,
        size=50,
        pages=1,
    )


@pytest.fixture
def mock_empty_users_page():
    """Create a mock empty paginated users response."""
    return Page(
        items=[],
        total=0,
        page=1,
        size=50,
        pages=0,
    )


@pytest.fixture
def mock_user_service(mock_users_page):
    """Create a mock UserService."""
    mock_service = AsyncMock()
    mock_service.get_all_users.return_value = mock_users_page
    return mock_service


@pytest.fixture
def mock_token():
    """Return a mock token string."""
    return "Bearer test_jwt_token_12345"


@pytest.fixture
def override_oauth2_scheme(app, mock_token):
    """Override oauth2_scheme to return a mock token."""
    app.dependency_overrides[oauth2_scheme] = lambda: mock_token
    yield
    app.dependency_overrides.pop(oauth2_scheme, None)


@pytest.fixture
def override_user_service(app, mock_user_service):
    """Override the user service dependency."""
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    yield
    app.dependency_overrides.pop(get_user_service, None)


@pytest.fixture
def override_current_user_info(app, mock_user):
    """Override the get_current_user_info dependency."""
    app.dependency_overrides[get_current_user_info] = lambda: mock_user
    yield
    app.dependency_overrides.pop(get_current_user_info, None)


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


### TESTS ###


### GET /users/me endpoint tests ###
@pytest.mark.unit
class TestGetMeEndpoint:
    """Tests for the GET /users/me endpoint."""

    @pytest.mark.asyncio
    async def test_get_me_success(
        self, client, override_oauth2_scheme, override_current_user_info, mock_user
    ):
        """Test successful retrieval of current user information."""
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer test_jwt_token_12345"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_uuid"] == mock_user.user_uuid
        assert data["email"] == mock_user.email
        assert data["is_active"] == mock_user.is_active
        assert data["role"] == mock_user.role.value

    @pytest.mark.asyncio
    async def test_get_me_returns_admin_user(
        self, client, app, mock_admin_user, override_oauth2_scheme
    ):
        """Test retrieval of admin user information."""
        app.dependency_overrides[get_current_user_info] = lambda: mock_admin_user

        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer test_jwt_token_12345"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == mock_admin_user.email
        assert data["role"] == UserRole.ADMIN.value

        app.dependency_overrides.pop(get_current_user_info, None)

    @pytest.mark.asyncio
    async def test_get_me_returns_inactive_user(
        self, client, app, mock_inactive_user, override_oauth2_scheme
    ):
        """Test retrieval of inactive user information."""
        app.dependency_overrides[get_current_user_info] = lambda: mock_inactive_user

        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer test_jwt_token_12345"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

        app.dependency_overrides.pop(get_current_user_info, None)

    @pytest.mark.asyncio
    async def test_get_me_missing_authorization_header(self, client):
        """Test GET /users/me without authorization header."""
        response = client.get("/users/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_returns_none_user_raises_error(
        self, client, app, override_oauth2_scheme
    ):
        """Test GET /users/me when user info is None raises validation error.

        When the dependency returns None but the response_model expects a GetUserResponseDto,
        FastAPI should raise a ResponseValidationError.
        """
        app.dependency_overrides[get_current_user_info] = lambda: None

        # This should raise an error since response_model=GetUserResponseDto doesn't allow None
        with pytest.raises(Exception):
            client.get(
                "/users/me",
                headers={"Authorization": "Bearer test_jwt_token_12345"},
            )

        app.dependency_overrides.pop(get_current_user_info, None)


### GET /users endpoint tests ###
@pytest.mark.unit
class TestGetAllUsersEndpoint:
    """Tests for the GET /users endpoint."""

    @pytest.mark.asyncio
    async def test_get_all_users_success(
        self,
        client,
        override_oauth2_scheme,
        override_user_service,
        mock_user,
        mock_admin_user,
    ):
        """Test successful retrieval of all users."""
        response = client.get(
            "/users",
            headers={"Authorization": "Bearer test_jwt_token_12345"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert data["total"] == 2
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_get_all_users_empty_list(
        self, client, app, mock_empty_users_page, override_oauth2_scheme
    ):
        """Test retrieval when no users exist."""
        mock_service = AsyncMock()
        mock_service.get_all_users.return_value = mock_empty_users_page
        app.dependency_overrides[get_user_service] = lambda: mock_service

        response = client.get(
            "/users",
            headers={"Authorization": "Bearer test_jwt_token_12345"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

        app.dependency_overrides.pop(get_user_service, None)

    @pytest.mark.asyncio
    async def test_get_all_users_with_pagination_params(
        self, client, app, mock_user_service, override_oauth2_scheme
    ):
        """Test retrieval with custom pagination parameters."""
        app.dependency_overrides[get_user_service] = lambda: mock_user_service

        response = client.get(
            "/users",
            params={"page": 1, "size": 10},
            headers={"Authorization": "Bearer test_jwt_token_12345"},
        )

        assert response.status_code == 200
        mock_user_service.get_all_users.assert_called_once()

        app.dependency_overrides.pop(get_user_service, None)

    @pytest.mark.asyncio
    async def test_get_all_users_calls_service_with_params(
        self, client, app, mock_user_service, override_oauth2_scheme
    ):
        """Test that get_all_users endpoint calls the service with correct params."""
        app.dependency_overrides[get_user_service] = lambda: mock_user_service

        response = client.get(
            "/users",
            headers={"Authorization": "Bearer test_jwt_token_12345"},
        )

        assert response.status_code == 200
        mock_user_service.get_all_users.assert_called_once()
        # Verify that Params object was passed
        call_args = mock_user_service.get_all_users.call_args
        assert call_args is not None

        app.dependency_overrides.pop(get_user_service, None)

    @pytest.mark.asyncio
    async def test_get_all_users_missing_authorization_header(self, client):
        """Test GET /users without authorization header."""
        response = client.get("/users")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_all_users_invalid_page_param(
        self, client, override_oauth2_scheme, override_user_service
    ):
        """Test GET /users with invalid page parameter."""
        response = client.get(
            "/users",
            params={"page": 0},  # Page should be >= 1
            headers={"Authorization": "Bearer test_jwt_token_12345"},
        )

        # fastapi-pagination should return a validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_all_users_invalid_size_param(
        self, client, override_oauth2_scheme, override_user_service
    ):
        """Test GET /users with invalid size parameter."""
        response = client.get(
            "/users",
            params={"size": 0},  # Size should be >= 1
            headers={"Authorization": "Bearer test_jwt_token_12345"},
        )

        # fastapi-pagination should return a validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_all_users_large_page_number(
        self, client, app, mock_empty_users_page, override_oauth2_scheme
    ):
        """Test GET /users with a large page number (no users on that page)."""
        mock_service = AsyncMock()
        mock_service.get_all_users.return_value = mock_empty_users_page
        app.dependency_overrides[get_user_service] = lambda: mock_service

        response = client.get(
            "/users",
            params={"page": 999},
            headers={"Authorization": "Bearer test_jwt_token_12345"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0

        app.dependency_overrides.pop(get_user_service, None)

"""
Tests for the authentication API endpoints defined in auth_router.py. This includes
tests for both the /auth/register and /auth/login endpoints, covering successful cases,
validation errors, and expected exceptions.
"""

from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import UUID4

from backend.api.auth.auth_dependencies import get_auth_service
from backend.api.auth.auth_dtos import (LoginResponseDto, RegisterRequestDto,
                                        RegisterResponseDto)
from backend.api.auth.auth_exceptions import (InvalidCredentialsException,
                                              UserCreateInternalErrorException,
                                              UserExistsException)
from backend.api.auth.auth_router import router


### FIXTURES ###
@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def mock_register_user_response():
    return RegisterResponseDto(
        id=UUID4("a400b358-71ca-4f15-9c9e-2193ebf9c06b"), email="admin@example.com"
    )


@pytest.fixture
def mock_login_response():
    return LoginResponseDto(
        access_token="test_jwt_token_12345",
        token_type="bearer",
    )


@pytest.fixture
def mock_auth_service(mock_register_user_response, mock_login_response):
    mock_auth_service = AsyncMock()
    mock_auth_service.add_new_user.return_value = mock_register_user_response
    mock_auth_service.login.return_value = mock_login_response
    return mock_auth_service


@pytest.fixture
def override_auth_service(app, mock_auth_service):
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(app, mock_auth_service):
    return TestClient(app)


### TESTS ###


@pytest.mark.unit
class TestRegisterEndpoint:
    """Tests for POST /auth/register endpoint."""

    @pytest.mark.asyncio
    async def test_register_user_success(
        self, client, override_auth_service, mock_auth_service
    ):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={"email": "admin@example.com", "password": "securepassword"},
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == "admin@example.com"
        mock_auth_service.add_new_user.assert_called_once_with(
            user=RegisterRequestDto(
                email="admin@example.com", password="securepassword"
            )
        )

    @pytest.mark.asyncio
    async def test_register_user_already_exists(self, client, app, mock_auth_service):
        """Test registration when user already exists."""
        mock_auth_service.add_new_user.side_effect = UserExistsException(
            "admin@example.com"
        )
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        response = client.post(
            "/auth/register",
            json={"email": "admin@example.com", "password": "securepassword"},
        )

        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"].lower()

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_user_internal_error(self, client, app, mock_auth_service):
        """Test registration when an internal error occurs."""
        mock_auth_service.add_new_user.side_effect = UserCreateInternalErrorException(
            detail="Database connection error"
        )
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        response = client.post(
            "/auth/register",
            json={"email": "admin@example.com", "password": "securepassword"},
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_user_invalid_email_format(
        self, client, override_auth_service
    ):
        """Test registration with invalid email format."""
        response = client.post(
            "/auth/register",
            json={"email": "invalid-email", "password": "securepassword"},
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_user_password_too_short(
        self, client, override_auth_service
    ):
        """Test registration with password that is too short."""
        response = client.post(
            "/auth/register",
            json={"email": "admin@example.com", "password": "short"},
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_user_missing_email(self, client, override_auth_service):
        """Test registration with missing email field."""
        response = client.post(
            "/auth/register",
            json={"password": "securepassword"},
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_user_missing_password(self, client, override_auth_service):
        """Test registration with missing password field."""
        response = client.post(
            "/auth/register",
            json={"email": "admin@example.com"},
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_user_empty_body(self, client, override_auth_service):
        """Test registration with empty request body."""
        response = client.post(
            "/auth/register",
            json={},
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.unit
class TestLoginEndpoint:
    """Tests for POST /auth/login endpoint."""

    @pytest.mark.asyncio
    async def test_login_user_success(self, client, override_auth_service):
        """Test successful user login."""
        response = client.post(
            "/auth/login",
            data={"username": "admin@example.com", "password": "securepassword"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["access_token"] == "test_jwt_token_12345"

    @pytest.mark.asyncio
    async def test_login_user_invalid_credentials(self, client, app, mock_auth_service):
        """Test login with invalid credentials."""
        mock_auth_service.login.side_effect = InvalidCredentialsException()
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        response = client.post(
            "/auth/login",
            data={"username": "admin@example.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_user_nonexistent_user(self, client, app, mock_auth_service):
        """Test login with a non-existent user."""
        mock_auth_service.login.side_effect = InvalidCredentialsException()
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        response = client.post(
            "/auth/login",
            data={"username": "nonexistent@example.com", "password": "securepassword"},
        )

        assert response.status_code == 401

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_user_missing_username(self, client, override_auth_service):
        """Test login with missing username field."""
        response = client.post(
            "/auth/login",
            data={"password": "securepassword"},
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_user_missing_password(self, client, override_auth_service):
        """Test login with missing password field."""
        response = client.post(
            "/auth/login",
            data={"username": "admin@example.com"},
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_user_empty_body(self, client, override_auth_service):
        """Test login with empty request body."""
        response = client.post(
            "/auth/login",
            data={},
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_calls_auth_service_with_correct_data(
        self, client, app, mock_auth_service, mock_login_response
    ):
        """Test that login endpoint calls auth service with correct data."""
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        response = client.post(
            "/auth/login",
            data={"username": "test@example.com", "password": "securepassword123"},
        )

        assert response.status_code == 200
        mock_auth_service.login.assert_called_once()
        call_args = mock_auth_service.login.call_args[0][0]
        assert call_args.username == "test@example.com"
        assert call_args.password == "securepassword123"

        app.dependency_overrides.clear()

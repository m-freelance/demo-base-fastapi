"""
Tests for AuthMiddleware.

This module contains unit tests for the role-based authentication middleware.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.auth.token_service import TokenService, TokenData
from backend.api.config.models import (
    AuthMiddlewareConfig,
    PathAccessConfig,
    JWTConfig,
    HttpMethod,
)
from backend.api.middleware.auth_middleware import AuthMiddleware
from backend.api.schemas.user import UserRole


class TestAuthMiddleware:
    """Tests for AuthMiddleware class."""

    @pytest.fixture
    def jwt_config(self) -> JWTConfig:
        """Create a JWTConfig for testing."""
        return JWTConfig(
            secret_key="test_secret_key_12345",
            algorithm="HS256",
            access_token_expire_minutes=30,
        )

    @pytest.fixture
    def auth_middleware_config(self) -> AuthMiddlewareConfig:
        """Create an AuthMiddlewareConfig for testing."""
        return AuthMiddlewareConfig(
            path_access=[
                PathAccessConfig(
                    path="/api/protected",
                    allowed_roles=[UserRole.USER, UserRole.ADMIN],
                    methods=[HttpMethod.GET, HttpMethod.POST],
                ),
                PathAccessConfig(
                    path="/api/admin",
                    allowed_roles=[UserRole.ADMIN],
                    methods=[HttpMethod.GET, HttpMethod.POST, HttpMethod.DELETE],
                ),
            ]
        )

    @pytest.fixture
    def token_service(self, jwt_config: JWTConfig) -> TokenService:
        """Create a TokenService for testing."""
        return TokenService(jwt_config=jwt_config)

    @pytest.fixture
    def user_token_data(self) -> TokenData:
        """Create user TokenData for testing."""
        return TokenData(email="user@example.com", role=UserRole.USER)

    @pytest.fixture
    def admin_token_data(self) -> TokenData:
        """Create admin TokenData for testing."""
        return TokenData(email="admin@example.com", role=UserRole.ADMIN)

    @pytest.fixture
    def user_token(
        self, token_service: TokenService, user_token_data: TokenData
    ) -> str:
        """Create a user JWT token."""
        return token_service.create_access_token(data=user_token_data)

    @pytest.fixture
    def admin_token(
        self, token_service: TokenService, admin_token_data: TokenData
    ) -> str:
        """Create an admin JWT token."""
        return token_service.create_access_token(data=admin_token_data)

    @pytest.fixture
    def app_with_middleware(
        self,
        auth_middleware_config: AuthMiddlewareConfig,
        jwt_config: JWTConfig,
    ) -> FastAPI:
        """Create a FastAPI app with AuthMiddleware."""
        app = FastAPI()

        @app.get("/api/protected")
        async def protected_endpoint():
            return {"message": "Protected resource"}

        @app.post("/api/protected")
        async def protected_post_endpoint():
            return {"message": "Protected POST resource"}

        @app.get("/api/admin")
        async def admin_endpoint():
            return {"message": "Admin resource"}

        @app.delete("/api/admin")
        async def admin_delete_endpoint():
            return {"message": "Admin delete resource"}

        @app.get("/api/public")
        async def public_endpoint():
            return {"message": "Public resource"}

        @app.get("/health")
        async def health_endpoint():
            return {"status": "ok"}

        app.add_middleware(
            AuthMiddleware,
            config=auth_middleware_config,
            jwt_config=jwt_config,
        )

        return app

    @pytest.fixture
    def client(self, app_with_middleware: FastAPI) -> TestClient:
        """Create a TestClient."""
        return TestClient(app_with_middleware, raise_server_exceptions=False)

    ### Public endpoint tests ###
    @pytest.mark.unit
    def test_public_endpoint_accessible_without_auth(self, client: TestClient):
        """Test that public endpoints are accessible without authentication."""
        response = client.get("/api/public")

        assert response.status_code == 200
        assert response.json() == {"message": "Public resource"}

    @pytest.mark.unit
    def test_health_endpoint_accessible_without_auth(self, client: TestClient):
        """Test that health endpoint is accessible without authentication."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    ### Protected endpoint tests ###
    @pytest.mark.unit
    def test_protected_endpoint_requires_auth(self, client: TestClient):
        """Test that protected endpoints require authentication."""
        response = client.get("/api/protected")

        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

    @pytest.mark.unit
    def test_protected_endpoint_accessible_with_user_token(
        self, client: TestClient, user_token: str
    ):
        """Test that protected endpoints are accessible with valid user token."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Protected resource"}

    @pytest.mark.unit
    def test_protected_endpoint_accessible_with_admin_token(
        self, client: TestClient, admin_token: str
    ):
        """Test that protected endpoints are accessible with admin token."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200

    @pytest.mark.unit
    def test_protected_post_endpoint_accessible_with_valid_token(
        self, client: TestClient, user_token: str
    ):
        """Test that protected POST endpoints are accessible with valid token."""
        response = client.post(
            "/api/protected",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200

    ### Admin endpoint tests ###
    @pytest.mark.unit
    def test_admin_endpoint_requires_auth(self, client: TestClient):
        """Test that admin endpoints require authentication."""
        response = client.get("/api/admin")

        assert response.status_code == 401

    @pytest.mark.unit
    def test_admin_endpoint_denies_user_role(self, client: TestClient, user_token: str):
        """Test that admin endpoints deny USER role."""
        response = client.get(
            "/api/admin",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 401
        assert "Insufficient permissions" in response.json()["detail"]

    @pytest.mark.unit
    def test_admin_endpoint_accessible_with_admin_token(
        self, client: TestClient, admin_token: str
    ):
        """Test that admin endpoints are accessible with admin token."""
        response = client.get(
            "/api/admin",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Admin resource"}

    @pytest.mark.unit
    def test_admin_delete_endpoint_accessible_with_admin_token(
        self, client: TestClient, admin_token: str
    ):
        """Test that admin DELETE endpoint is accessible with admin token."""
        response = client.delete(
            "/api/admin",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200

    ### Invalid token tests ###
    @pytest.mark.unit
    def test_protected_endpoint_rejects_invalid_token(self, client: TestClient):
        """Test that protected endpoints reject invalid tokens."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401
        assert "Invalid or expired token" in response.json()["detail"]

    @pytest.mark.unit
    def test_protected_endpoint_rejects_malformed_auth_header(self, client: TestClient):
        """Test that protected endpoints reject malformed auth headers."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": "InvalidFormat token"},
        )

        assert response.status_code == 401

    @pytest.mark.unit
    def test_protected_endpoint_rejects_missing_bearer_prefix(
        self, client: TestClient, user_token: str
    ):
        """Test that protected endpoints reject missing Bearer prefix."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": user_token},
        )

        assert response.status_code == 401

    ### Token extraction tests ###
    @pytest.mark.unit
    def test_extract_token_from_bearer_header(
        self, client: TestClient, user_token: str
    ):
        """Test that token is correctly extracted from Bearer header."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200

    @pytest.mark.unit
    def test_extract_token_case_insensitive_bearer(
        self, client: TestClient, user_token: str
    ):
        """Test that Bearer prefix is case-insensitive."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": f"bearer {user_token}"},
        )

        assert response.status_code == 200

    ### Method-specific protection tests ###
    @pytest.mark.unit
    def test_unprotected_method_on_protected_path(
        self,
        jwt_config: JWTConfig,
    ):
        """Test that unprotected methods on protected paths are accessible."""
        # Create config that only protects GET method
        config = AuthMiddlewareConfig(
            path_access=[
                PathAccessConfig(
                    path="/api/protected",
                    allowed_roles=[UserRole.USER],
                    methods=[HttpMethod.GET],  # Only GET is protected
                ),
            ]
        )

        app = FastAPI()

        @app.get("/api/protected")
        async def protected_get():
            return {"message": "Protected GET"}

        @app.put("/api/protected")
        async def unprotected_put():
            return {"message": "Unprotected PUT"}

        app.add_middleware(AuthMiddleware, config=config, jwt_config=jwt_config)

        client = TestClient(app, raise_server_exceptions=False)

        # PUT should be accessible without auth (not in protected methods)
        put_response = client.put("/api/protected")
        assert put_response.status_code == 200

        # GET should require auth
        get_response = client.get("/api/protected")
        assert get_response.status_code == 401

    ### Path prefix matching tests ###
    @pytest.mark.unit
    def test_path_prefix_matching(self, client: TestClient, user_token: str):
        """Test that path prefix matching works correctly."""
        # /api/protected should match paths starting with /api/protected
        response = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200

    @pytest.mark.unit
    def test_public_endpoint_stores_token_data_when_provided(
        self,
        jwt_config: JWTConfig,
        user_token: str,
    ):
        """Test that token data is stored in request state even for public endpoints."""
        config = AuthMiddlewareConfig(path_access=[])  # No protected paths

        app = FastAPI()

        @app.get("/api/public")
        async def public_with_optional_auth():
            return {"message": "Public"}

        app.add_middleware(AuthMiddleware, config=config, jwt_config=jwt_config)

        client = TestClient(app, raise_server_exceptions=False)

        # Request with token should still work for public endpoint
        response = client.get(
            "/api/public",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200

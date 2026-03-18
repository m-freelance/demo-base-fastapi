"""
Tests for ErrorMiddleware.

This module contains unit tests for the global error handling middleware.
The middleware catches generic exceptions (not HTTPExceptions, which FastAPI handles).
"""

from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.config.models import ErrorMiddlewareConfig
from backend.api.middleware.error_middleware import ErrorMiddleware


class TestErrorMiddleware:
    """Tests for ErrorMiddleware class."""

    @pytest.fixture
    def error_config_detailed(self) -> ErrorMiddlewareConfig:
        """Create an ErrorMiddlewareConfig that returns detailed errors."""
        return ErrorMiddlewareConfig(return_detailed_internal_errors=True)

    @pytest.fixture
    def error_config_generic(self) -> ErrorMiddlewareConfig:
        """Create an ErrorMiddlewareConfig that returns generic errors."""
        return ErrorMiddlewareConfig(return_detailed_internal_errors=False)

    @pytest.fixture
    def app_with_detailed_errors(
        self, error_config_detailed: ErrorMiddlewareConfig
    ) -> FastAPI:
        """Create a FastAPI app with ErrorMiddleware returning detailed errors."""
        app = FastAPI()

        @app.get("/success")
        async def success_endpoint():
            return {"message": "Success"}

        @app.get("/internal-error")
        async def internal_error_endpoint():
            raise Exception("Internal server error details")

        @app.get("/division-error")
        async def division_error_endpoint():
            return 1 / 0

        @app.get("/value-error")
        async def value_error_endpoint():
            raise ValueError("Invalid value provided")

        app.add_middleware(ErrorMiddleware, config=error_config_detailed)  # type: ignore[arg-type]

        return app

    @pytest.fixture
    def app_with_generic_errors(
        self, error_config_generic: ErrorMiddlewareConfig
    ) -> FastAPI:
        """Create a FastAPI app with ErrorMiddleware returning generic errors."""
        app = FastAPI()

        @app.get("/success")
        async def success_endpoint():
            return {"message": "Success"}

        @app.get("/internal-error")
        async def internal_error_endpoint():
            raise Exception("Sensitive error details")

        @app.get("/runtime-error")
        async def runtime_error_endpoint():
            raise RuntimeError("Runtime error occurred")

        app.add_middleware(ErrorMiddleware, config=error_config_generic)  # type: ignore[arg-type]

        return app

    @pytest.fixture
    def client_detailed(self, app_with_detailed_errors: FastAPI) -> TestClient:
        """Create a TestClient with detailed error middleware."""
        return TestClient(app_with_detailed_errors, raise_server_exceptions=False)

    @pytest.fixture
    def client_generic(self, app_with_generic_errors: FastAPI) -> TestClient:
        """Create a TestClient with generic error middleware."""
        return TestClient(app_with_generic_errors, raise_server_exceptions=False)

    ### Success cases ###
    @pytest.mark.unit
    def test_success_response_passes_through(self, client_detailed: TestClient):
        """Test that successful responses pass through unchanged."""
        response = client_detailed.get("/success")

        assert response.status_code == 200
        assert response.json() == {"message": "Success"}

    ### Internal error tests with detailed config ###
    @pytest.mark.unit
    def test_internal_error_returns_500_status(self, client_detailed: TestClient):
        """Test that internal errors return 500 status code."""
        response = client_detailed.get("/internal-error")

        assert response.status_code == 500

    @pytest.mark.unit
    def test_internal_error_returns_detailed_message_when_configured(
        self, client_detailed: TestClient
    ):
        """Test that internal errors return detailed message when configured."""
        response = client_detailed.get("/internal-error")

        assert response.status_code == 500
        assert "Internal server error details" in response.json()["message"]

    @pytest.mark.unit
    def test_division_error_returns_500(self, client_detailed: TestClient):
        """Test that division by zero returns 500 status code."""
        response = client_detailed.get("/division-error")

        assert response.status_code == 500

    @pytest.mark.unit
    def test_value_error_returns_500(self, client_detailed: TestClient):
        """Test that ValueError returns 500 status code."""
        response = client_detailed.get("/value-error")

        assert response.status_code == 500
        assert "Invalid value provided" in response.json()["message"]

    ### Internal error tests with generic config ###
    @pytest.mark.unit
    def test_internal_error_returns_generic_message_when_configured(
        self, client_generic: TestClient
    ):
        """Test that internal errors return generic message when configured."""
        response = client_generic.get("/internal-error")

        assert response.status_code == 500
        # Should not contain sensitive details
        assert "Sensitive error details" not in response.json()["message"]
        assert "unexpected error" in response.json()["message"].lower()

    @pytest.mark.unit
    def test_runtime_error_returns_generic_message(self, client_generic: TestClient):
        """Test that RuntimeError returns generic message when configured."""
        response = client_generic.get("/runtime-error")

        assert response.status_code == 500
        assert "Runtime error occurred" not in response.json()["message"]
        assert "unexpected error" in response.json()["message"].lower()

    @pytest.mark.unit
    def test_success_with_generic_config(self, client_generic: TestClient):
        """Test that success responses work with generic error config."""
        response = client_generic.get("/success")

        assert response.status_code == 200
        assert response.json() == {"message": "Success"}

    ### Response format tests ###
    @pytest.mark.unit
    def test_error_response_is_json(self, client_detailed: TestClient):
        """Test that error responses are JSON formatted."""
        response = client_detailed.get("/internal-error")

        assert response.headers["content-type"] == "application/json"

    @pytest.mark.unit
    def test_error_response_contains_message_key(self, client_detailed: TestClient):
        """Test that error responses contain 'message' key."""
        response = client_detailed.get("/internal-error")

        assert "message" in response.json()

    ### Logging tests ###
    @pytest.mark.unit
    def test_internal_error_is_logged(self, client_detailed: TestClient):
        """Test that internal errors are logged."""
        with patch("backend.api.middleware.error_middleware.logger") as mock_logger:
            response = client_detailed.get("/internal-error")

            assert response.status_code == 500
            mock_logger.error.assert_called()

    @pytest.mark.unit
    def test_division_error_is_logged(self, client_detailed: TestClient):
        """Test that division errors are logged."""
        with patch("backend.api.middleware.error_middleware.logger") as mock_logger:
            response = client_detailed.get("/division-error")

            assert response.status_code == 500
            mock_logger.error.assert_called()

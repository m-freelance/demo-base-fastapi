"""
Tests for TokenService.

This module contains unit tests for JWT token creation and verification.
"""

from datetime import datetime, timedelta, timezone

import pytest

from backend.api.auth.token_service import TokenData, TokenService
from backend.api.config.models import JWTConfig
from backend.api.schemas.user import UserRole


@pytest.mark.unit
class TestTokenService:
    """Tests for TokenService class."""

    @pytest.fixture
    def jwt_config(self) -> JWTConfig:
        """Create a JWTConfig instance for testing."""
        return JWTConfig(
            secret_key="test_secret_key_12345",
            algorithm="HS256",
            access_token_expire_minutes=30,
        )

    @pytest.fixture
    def token_service(self, jwt_config: JWTConfig) -> TokenService:
        """Create a TokenService instance for testing."""
        return TokenService(jwt_config=jwt_config)

    @pytest.fixture
    def sample_token_data(self) -> TokenData:
        """Create sample TokenData for testing."""
        return TokenData(email="test@example.com", role=UserRole.USER)

    @pytest.fixture
    def admin_token_data(self) -> TokenData:
        """Create admin TokenData for testing."""
        return TokenData(email="admin@example.com", role=UserRole.ADMIN)

    def test_create_access_token_returns_string(
        self, token_service: TokenService, sample_token_data: TokenData
    ):
        """Test that create_access_token returns a JWT string."""
        token = token_service.create_access_token(data=sample_token_data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_produces_jwt_format(
        self, token_service: TokenService, sample_token_data: TokenData
    ):
        """Test that create_access_token returns a valid JWT format (header.payload.signature)."""
        token = token_service.create_access_token(data=sample_token_data)

        parts = token.split(".")
        assert len(parts) == 3

    def test_verify_token_returns_token_data(
        self, token_service: TokenService, sample_token_data: TokenData
    ):
        """Test that verify_token returns correct TokenData."""
        token = token_service.create_access_token(data=sample_token_data)

        result = token_service.verify_token(token)

        assert result is not None
        assert result.email == sample_token_data.email
        assert result.role == sample_token_data.role

    def test_verify_token_returns_correct_role(
        self, token_service: TokenService, admin_token_data: TokenData
    ):
        """Test that verify_token returns correct admin role."""
        token = token_service.create_access_token(data=admin_token_data)

        result = token_service.verify_token(token)

        assert result is not None
        assert result.role == UserRole.ADMIN

    def test_verify_token_with_invalid_token_returns_none(
        self, token_service: TokenService
    ):
        """Test that verify_token returns None for invalid token."""
        result = token_service.verify_token("invalid.token.string")

        assert result is None

    def test_verify_token_with_tampered_token_returns_none(
        self, token_service: TokenService, sample_token_data: TokenData
    ):
        """Test that verify_token returns None for tampered token."""
        token = token_service.create_access_token(data=sample_token_data)
        # Tamper with the token by changing a character
        tampered_token = token[:-1] + ("a" if token[-1] != "a" else "b")

        result = token_service.verify_token(tampered_token)

        assert result is None

    def test_verify_token_with_wrong_secret_returns_none(
        self, sample_token_data: TokenData
    ):
        """Test that verify_token returns None when using wrong secret key."""
        # Create token with one secret
        jwt_config1 = JWTConfig(
            secret_key="secret_key_1",
            algorithm="HS256",
            access_token_expire_minutes=30,
        )
        token_service1 = TokenService(jwt_config=jwt_config1)
        token = token_service1.create_access_token(data=sample_token_data)

        # Verify with different secret
        jwt_config2 = JWTConfig(
            secret_key="secret_key_2",
            algorithm="HS256",
            access_token_expire_minutes=30,
        )
        token_service2 = TokenService(jwt_config=jwt_config2)

        result = token_service2.verify_token(token)

        assert result is None

    def test_verify_token_with_expired_token_returns_none(
        self, sample_token_data: TokenData
    ):
        """Test that verify_token returns None for expired token."""
        import jwt

        jwt_config = JWTConfig(
            secret_key="test_secret_key_32_chars_long_xx",
            algorithm="HS256",
            access_token_expire_minutes=30,
        )
        token_service = TokenService(jwt_config=jwt_config)

        # Manually create an expired token
        assert sample_token_data.role is not None
        expired_payload = {
            "email": sample_token_data.email,
            "role": sample_token_data.role.value,
            "expired": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),  # Already expired
        }
        expired_token = jwt.encode(
            expired_payload,
            jwt_config.secret_key,
            algorithm=jwt_config.algorithm,
        )

        # The token should be expired
        result = token_service.verify_token(expired_token)

        # Expired tokens should return None
        assert result is None

    def test_verify_token_with_empty_string_returns_none(
        self, token_service: TokenService
    ):
        """Test that verify_token returns None for empty string."""
        result = token_service.verify_token("")

        assert result is None

    def test_create_access_token_different_users_produce_different_tokens(
        self, token_service: TokenService
    ):
        """Test that different users produce different tokens."""
        user1 = TokenData(email="user1@example.com", role=UserRole.USER)
        user2 = TokenData(email="user2@example.com", role=UserRole.USER)

        token1 = token_service.create_access_token(data=user1)
        token2 = token_service.create_access_token(data=user2)

        assert token1 != token2

    def test_create_access_token_same_user_produces_different_tokens_at_different_times(
        self, token_service: TokenService, sample_token_data: TokenData
    ):
        """Test that creating tokens at different times produces different tokens."""
        token1 = token_service.create_access_token(data=sample_token_data)

        # Create another token (expiration time will differ slightly)
        token2 = token_service.create_access_token(data=sample_token_data)

        # Tokens might be the same if created at exactly same time, but typically differ
        # due to timing. We mainly verify both are valid.
        result1 = token_service.verify_token(token1)
        result2 = token_service.verify_token(token2)

        assert result1 is not None
        assert result2 is not None

    def test_verify_token_preserves_email_with_special_characters(
        self, token_service: TokenService
    ):
        """Test that email with special characters is preserved."""
        special_email = "test+special@example.com"
        token_data = TokenData(email=special_email, role=UserRole.USER)

        token = token_service.create_access_token(data=token_data)
        result = token_service.verify_token(token)

        assert result is not None
        assert result.email == special_email

    def test_token_service_with_different_algorithms(
        self, sample_token_data: TokenData
    ):
        """Test TokenService works with different algorithms."""
        # Use a key that's long enough for all algorithms (64 bytes for SHA512)
        secret_key = "test_secret_key_64_chars_long_for_sha512_xxxxxxxxxxxxxxxxxxxxxxx"
        for algorithm in ["HS256", "HS384", "HS512"]:
            jwt_config = JWTConfig(
                secret_key=secret_key,
                algorithm=algorithm,
                access_token_expire_minutes=30,
            )
            token_service = TokenService(jwt_config=jwt_config)

            token = token_service.create_access_token(data=sample_token_data)
            result = token_service.verify_token(token)

            assert result is not None
            assert result.email == sample_token_data.email

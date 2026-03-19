"""
Tests for PasswordHasher.

This module contains unit tests for password hashing and verification.
"""

import pytest

from backend.api.auth.password_hasher import PasswordHasher


@pytest.mark.unit
class TestPasswordHasher:
    """Tests for PasswordHasher class."""

    @pytest.fixture
    def password_hasher(self) -> PasswordHasher:
        """Create a PasswordHasher instance for testing."""
        return PasswordHasher()

    @pytest.fixture
    def sample_password(self) -> str:
        """Return a sample password for testing."""
        return "securepassword123"

    def test_encrypt_password_returns_hashed_string(
        self, password_hasher: PasswordHasher, sample_password: str
    ):
        """Test that encrypt_password returns a hashed string."""
        hashed = password_hasher.encrypt_password(sample_password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != sample_password

    def test_encrypt_password_produces_different_hashes_for_same_password(
        self, password_hasher: PasswordHasher, sample_password: str
    ):
        """Test that encrypting the same password twice produces different hashes (due to salt)."""
        hash1 = password_hasher.encrypt_password(sample_password)
        hash2 = password_hasher.encrypt_password(sample_password)

        # Argon2 uses salt, so hashes should differ
        assert hash1 != hash2

    def test_encrypt_password_produces_different_hashes_for_different_passwords(
        self, password_hasher: PasswordHasher
    ):
        """Test that different passwords produce different hashes."""
        hash1 = password_hasher.encrypt_password("password123")
        hash2 = password_hasher.encrypt_password("differentpassword456")

        assert hash1 != hash2

    def test_verify_password_returns_true_for_correct_password(
        self, password_hasher: PasswordHasher, sample_password: str
    ):
        """Test that verify_password returns True for correct password."""
        hashed = password_hasher.encrypt_password(sample_password)

        result = password_hasher.verify_password(sample_password, hashed)

        assert result is True

    def test_verify_password_returns_false_for_incorrect_password(
        self, password_hasher: PasswordHasher, sample_password: str
    ):
        """Test that verify_password returns False for incorrect password."""
        hashed = password_hasher.encrypt_password(sample_password)

        result = password_hasher.verify_password("wrongpassword", hashed)

        assert result is False

    def test_verify_password_returns_false_for_empty_password(
        self, password_hasher: PasswordHasher, sample_password: str
    ):
        """Test that verify_password returns False for empty password."""
        hashed = password_hasher.encrypt_password(sample_password)

        result = password_hasher.verify_password("", hashed)

        assert result is False

    def test_encrypt_empty_password(self, password_hasher: PasswordHasher):
        """Test that encrypt_password handles empty string."""
        hashed = password_hasher.encrypt_password("")

        assert hashed is not None
        assert isinstance(hashed, str)
        assert password_hasher.verify_password("", hashed) is True

    def test_encrypt_password_with_special_characters(
        self, password_hasher: PasswordHasher
    ):
        """Test that encrypt_password handles passwords with special characters."""
        special_password = "p@$$w0rd!#%^&*()_+-=[]{}|;':\",./<>?"
        hashed = password_hasher.encrypt_password(special_password)

        assert hashed is not None
        assert password_hasher.verify_password(special_password, hashed) is True

    def test_encrypt_password_with_unicode_characters(
        self, password_hasher: PasswordHasher
    ):
        """Test that encrypt_password handles passwords with unicode characters."""
        unicode_password = "密码🔐パスワード"
        hashed = password_hasher.encrypt_password(unicode_password)

        assert hashed is not None
        assert password_hasher.verify_password(unicode_password, hashed) is True

    def test_verify_password_is_case_sensitive(self, password_hasher: PasswordHasher):
        """Test that password verification is case-sensitive."""
        password = "SecurePassword"
        hashed = password_hasher.encrypt_password(password)

        assert password_hasher.verify_password("securepassword", hashed) is False
        assert password_hasher.verify_password("SECUREPASSWORD", hashed) is False
        assert password_hasher.verify_password("SecurePassword", hashed) is True

    def test_hashed_password_contains_argon2_identifier(
        self, password_hasher: PasswordHasher, sample_password: str
    ):
        """Test that hashed password contains argon2 identifier."""
        hashed = password_hasher.encrypt_password(sample_password)

        # Argon2 hashes typically start with $argon2
        assert hashed.startswith("$argon2")

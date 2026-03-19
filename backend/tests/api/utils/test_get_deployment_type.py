"""
Tests for get_deployment_type utility.

This module contains unit tests for deployment type detection.
"""

import os
from unittest.mock import patch

import pytest

from backend.api.utils.get_deployment_type import DeploymentType, get_deployment_type


@pytest.mark.unit
class TestGetDeploymentType:
    """Tests for get_deployment_type function."""

    def test_returns_local_by_default(self):
        """Test that LOCAL is returned when DEPLOYMENT_TYPE is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove DEPLOYMENT_TYPE if it exists
            os.environ.pop("DEPLOYMENT_TYPE", None)

            result = get_deployment_type()

            assert result == DeploymentType.LOCAL

    def test_returns_local_when_set_to_local(self):
        """Test that LOCAL is returned when DEPLOYMENT_TYPE is 'local'."""
        with patch.dict(os.environ, {"DEPLOYMENT_TYPE": "local"}):
            result = get_deployment_type()

            assert result == DeploymentType.LOCAL

    def test_returns_test_when_set_to_test(self):
        """Test that TEST is returned when DEPLOYMENT_TYPE is 'test'."""
        with patch.dict(os.environ, {"DEPLOYMENT_TYPE": "test"}):
            result = get_deployment_type()

            assert result == DeploymentType.TEST

    def test_returns_development_when_set_to_dev(self):
        """Test that DEVELOPMENT is returned when DEPLOYMENT_TYPE is 'dev'."""
        with patch.dict(os.environ, {"DEPLOYMENT_TYPE": "dev"}):
            result = get_deployment_type()

            assert result == DeploymentType.DEVELOPMENT

    def test_returns_production_when_set_to_prod(self):
        """Test that PRODUCTION is returned when DEPLOYMENT_TYPE is 'prod'."""
        with patch.dict(os.environ, {"DEPLOYMENT_TYPE": "prod"}):
            result = get_deployment_type()

            assert result == DeploymentType.PRODUCTION

    def test_case_insensitive_local(self):
        """Test that deployment type detection is case-insensitive for LOCAL."""
        with patch.dict(os.environ, {"DEPLOYMENT_TYPE": "LOCAL"}):
            result = get_deployment_type()

            assert result == DeploymentType.LOCAL

    def test_case_insensitive_test(self):
        """Test that deployment type detection is case-insensitive for TEST."""
        with patch.dict(os.environ, {"DEPLOYMENT_TYPE": "TEST"}):
            result = get_deployment_type()

            assert result == DeploymentType.TEST

    def test_case_insensitive_dev(self):
        """Test that deployment type detection is case-insensitive for DEV."""
        with patch.dict(os.environ, {"DEPLOYMENT_TYPE": "DEV"}):
            result = get_deployment_type()

            assert result == DeploymentType.DEVELOPMENT

    def test_case_insensitive_prod(self):
        """Test that deployment type detection is case-insensitive for PROD."""
        with patch.dict(os.environ, {"DEPLOYMENT_TYPE": "PROD"}):
            result = get_deployment_type()

            assert result == DeploymentType.PRODUCTION

    def test_raises_error_for_invalid_deployment_type(self):
        """Test that ValueError is raised for invalid deployment type."""
        with patch.dict(os.environ, {"DEPLOYMENT_TYPE": "invalid"}):
            with pytest.raises(ValueError) as exc_info:
                get_deployment_type()

            assert "Invalid DEPLOYMENT_TYPE" in str(exc_info.value)
            assert "invalid" in str(exc_info.value)

    def test_error_message_contains_valid_options(self):
        """Test that error message contains list of valid options."""
        with patch.dict(os.environ, {"DEPLOYMENT_TYPE": "invalid"}):
            with pytest.raises(ValueError) as exc_info:
                get_deployment_type()

            error_message = str(exc_info.value)
            assert "local" in error_message
            assert "test" in error_message
            assert "dev" in error_message
            assert "prod" in error_message


@pytest.mark.unit
class TestDeploymentTypeEnum:
    """Tests for DeploymentType enum."""

    def test_local_value(self):
        """Test LOCAL enum value."""
        assert DeploymentType.LOCAL.value == "local"

    def test_test_value(self):
        """Test TEST enum value."""
        assert DeploymentType.TEST.value == "test"

    def test_development_value(self):
        """Test DEVELOPMENT enum value."""
        assert DeploymentType.DEVELOPMENT.value == "dev"

    def test_production_value(self):
        """Test PRODUCTION enum value."""
        assert DeploymentType.PRODUCTION.value == "prod"

    def test_all_deployment_types_exist(self):
        """Test that all expected deployment types exist."""
        expected_types = ["LOCAL", "TEST", "DEVELOPMENT", "PRODUCTION"]

        for type_name in expected_types:
            assert hasattr(DeploymentType, type_name)

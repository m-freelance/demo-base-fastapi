"""
Tests for load_config module.

This module contains unit tests for configuration loading and parsing.
"""

import os
from unittest.mock import patch

import pytest

from backend.api.config.load_config import (
    deep_merge,
    replace_env_variables,
    parse_config,
    get_config_paths_for_deployment,
)
from backend.api.config.models import (
    ApplicationConfig,
    HttpMethod,
    LoggingLevel,
    LoggingHandlerType,
)
from backend.api.utils.get_deployment_type import DeploymentType
from backend.api.schemas.user import UserRole


class TestDeepMerge:
    """Tests for deep_merge function."""

    @pytest.mark.unit
    def test_merge_empty_dicts(self):
        """Test merging two empty dictionaries."""
        result = deep_merge({}, {})
        assert result == {}

    @pytest.mark.unit
    def test_merge_with_empty_base(self):
        """Test merging when base is empty."""
        result = deep_merge({}, {"key": "value"})
        assert result == {"key": "value"}

    @pytest.mark.unit
    def test_merge_with_empty_update(self):
        """Test merging when update is empty."""
        result = deep_merge({"key": "value"}, {})
        assert result == {"key": "value"}

    @pytest.mark.unit
    def test_simple_override(self):
        """Test that update values override base values."""
        result = deep_merge({"key": "old"}, {"key": "new"})
        assert result == {"key": "new"}

    @pytest.mark.unit
    def test_adds_new_keys(self):
        """Test that new keys from update are added."""
        result = deep_merge({"a": 1}, {"b": 2})
        assert result == {"a": 1, "b": 2}

    @pytest.mark.unit
    def test_nested_dict_merge(self):
        """Test that nested dicts are merged recursively."""
        base = {"outer": {"a": 1, "b": 2}}
        update = {"outer": {"b": 3, "c": 4}}
        result = deep_merge(base, update)
        assert result == {"outer": {"a": 1, "b": 3, "c": 4}}

    @pytest.mark.unit
    def test_deeply_nested_merge(self):
        """Test merging deeply nested structures."""
        base = {"l1": {"l2": {"l3": {"a": 1}}}}
        update = {"l1": {"l2": {"l3": {"b": 2}}}}
        result = deep_merge(base, update)
        assert result == {"l1": {"l2": {"l3": {"a": 1, "b": 2}}}}

    @pytest.mark.unit
    def test_list_replaced_not_merged(self):
        """Test that lists are replaced, not merged."""
        result = deep_merge({"items": [1, 2]}, {"items": [3, 4]})
        assert result == {"items": [3, 4]}

    @pytest.mark.unit
    def test_dict_replaced_by_scalar(self):
        """Test that dict can be replaced by scalar."""
        result = deep_merge({"key": {"nested": 1}}, {"key": "string"})
        assert result == {"key": "string"}

    @pytest.mark.unit
    def test_scalar_replaced_by_dict(self):
        """Test that scalar can be replaced by dict."""
        result = deep_merge({"key": "string"}, {"key": {"nested": 1}})
        assert result == {"key": {"nested": 1}}

    @pytest.mark.unit
    def test_base_not_mutated(self):
        """Test that base dict is not mutated."""
        base = {"key": "value"}
        deep_merge(base, {"key": "new"})
        assert base == {"key": "value"}


class TestReplaceEnvVariables:
    """Tests for replace_env_variables function."""

    @pytest.mark.unit
    def test_no_placeholders(self):
        """Test string without placeholders is unchanged."""
        result = replace_env_variables("plain string")
        assert result == "plain string"

    @pytest.mark.unit
    def test_single_replacement(self):
        """Test single env var replacement."""
        env = {"MY_VAR": "my_value"}
        result = replace_env_variables("prefix_${MY_VAR}_suffix", env.get)
        assert result == "prefix_my_value_suffix"

    @pytest.mark.unit
    def test_multiple_replacements(self):
        """Test multiple env var replacements."""
        env = {"A": "1", "B": "2"}
        result = replace_env_variables("${A}_${B}", env.get)
        assert result == "1_2"

    @pytest.mark.unit
    def test_missing_var_keeps_placeholder(self):
        """Test that missing env vars keep placeholder."""
        result = replace_env_variables("${MISSING}", lambda k: None)
        assert result == "${MISSING}"

    @pytest.mark.unit
    def test_nested_dict_replacement(self):
        """Test replacement in nested dicts."""
        env = {"VAL": "replaced"}
        data = {"outer": {"inner": "${VAL}"}}
        result = replace_env_variables(data, env.get)
        assert result == {"outer": {"inner": "replaced"}}

    @pytest.mark.unit
    def test_list_replacement(self):
        """Test replacement in lists."""
        env = {"A": "1", "B": "2"}
        result = replace_env_variables(["${A}", "${B}"], env.get)
        assert result == ["1", "2"]

    @pytest.mark.unit
    def test_non_string_unchanged(self):
        """Test that non-string values are unchanged."""
        result = replace_env_variables({"num": 123, "bool": True, "none": None})
        assert result == {"num": 123, "bool": True, "none": None}

    @pytest.mark.unit
    def test_empty_env_value(self):
        """Test env var with empty string value."""
        env = {"EMPTY": ""}
        result = replace_env_variables("${EMPTY}", env.get)
        assert result == ""


class TestParseConfig:
    """Tests for parse_config function."""

    @pytest.fixture
    def valid_config_dict(self) -> dict:
        """Return a valid configuration dictionary."""
        return {
            "api": {
                "title": "Test API",
                "host": "localhost",
                "port": 8000,
                "origins": [],
                "allow_credentials": True,
                "allow_methods": ["GET", "POST"],
                "database": {
                    "url": "postgresql://localhost/test",
                    "pool_size": 5,
                    "max_overflow": 10,
                    "pool_pre_ping": True,
                    "echo": False,
                },
                "middleware": {
                    "error_middleware": {"return_detailed_internal_errors": True},
                    "auth_middleware": {"path_access": []},
                },
                "jwt": {
                    "secret_key": "test-secret",
                    "algorithm": "HS256",
                    "access_token_expire_minutes": 30,
                },
            },
            "logging": {
                "level": "INFO",
                "format": "%(message)s",
                "date_format": "%Y-%m-%d",
                "handlers": ["console"],
                "file": {
                    "enabled": False,
                    "filename": "test.log",
                    "max_bytes": 1000,
                    "backup_count": 1,
                },
            },
        }

    @pytest.mark.unit
    def test_parses_valid_config(self, valid_config_dict):
        """Test parsing a valid config dict."""
        result = parse_config(valid_config_dict)
        assert isinstance(result, ApplicationConfig)
        assert result.api.title == "Test API"
        assert result.api.port == 8000

    @pytest.mark.unit
    def test_parses_enums_correctly(self, valid_config_dict):
        """Test that enum values are parsed correctly."""
        result = parse_config(valid_config_dict)
        assert HttpMethod.GET in result.api.allow_methods
        assert result.logging.level == LoggingLevel.INFO
        assert LoggingHandlerType.CONSOLE in result.logging.handlers

    @pytest.mark.unit
    def test_raises_on_missing_required_field(self):
        """Test that missing required fields raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_config({"api": {}})
        assert "Invalid configuration" in str(exc_info.value)

    @pytest.mark.unit
    def test_raises_on_invalid_enum_value(self, valid_config_dict):
        """Test that invalid enum values raise ValueError."""
        valid_config_dict["logging"]["level"] = "INVALID_LEVEL"
        with pytest.raises(ValueError):
            parse_config(valid_config_dict)

    @pytest.mark.unit
    def test_parses_path_access_with_roles(self, valid_config_dict):
        """Test parsing path_access with user roles."""
        valid_config_dict["api"]["middleware"]["auth_middleware"]["path_access"] = [
            {
                "path": "/api/users",
                "allowed_roles": ["admin", "user"],
                "methods": ["GET"],
            }
        ]
        result = parse_config(valid_config_dict)
        path_access = result.api.middleware.auth_middleware.path_access[0]
        assert UserRole.ADMIN in path_access.allowed_roles
        assert UserRole.USER in path_access.allowed_roles


class TestGetConfigPathsForDeployment:
    """Tests for get_config_paths_for_deployment function."""

    @pytest.mark.unit
    def test_local_returns_base_paths(self):
        """Test LOCAL deployment returns base config paths."""
        result = get_config_paths_for_deployment(DeploymentType.LOCAL)
        assert "resources/default_config.yaml" in result
        assert "resources/local_config.yaml" in result

    @pytest.mark.unit
    def test_test_returns_test_paths(self):
        """Test TEST deployment returns test config paths."""
        result = get_config_paths_for_deployment(DeploymentType.TEST)
        assert "resources/default_config.yaml" in result
        assert "resources/test_config.yaml" in result

    @pytest.mark.unit
    def test_prod_requires_config_paths_env(self):
        """Test PRODUCTION deployment requires CONFIG_PATHS env var."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("CONFIG_PATHS", None)
            with pytest.raises(ValueError) as exc_info:
                get_config_paths_for_deployment(DeploymentType.PRODUCTION)
            assert "CONFIG_PATHS" in str(exc_info.value)

    @pytest.mark.unit
    def test_prod_uses_config_paths_env(self):
        """Test PRODUCTION deployment uses CONFIG_PATHS env var."""
        with patch.dict(os.environ, {"CONFIG_PATHS": "a.yaml;b.yaml"}):
            result = get_config_paths_for_deployment(DeploymentType.PRODUCTION)
            assert result == ["a.yaml", "b.yaml"]

    @pytest.mark.unit
    def test_dev_requires_config_paths_env(self):
        """Test DEVELOPMENT deployment requires CONFIG_PATHS env var."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("CONFIG_PATHS", None)
            with pytest.raises(ValueError):
                get_config_paths_for_deployment(DeploymentType.DEVELOPMENT)

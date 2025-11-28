"""Tests for pydantic-file-settings."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

import pydantic_file_settings
from pydantic_file_settings import (
    BaseSettings,
    FileSettings,
    SettingsError,
    SettingsExistsError,
    SettingsNotFoundError,
)


class SimpleSettings(FileSettings):
    """Simple settings for testing."""

    name: str = "default"
    count: int = 0
    enabled: bool = True


class CustomFilenameSettings(FileSettings):
    """Settings with custom filename."""

    __FILENAME__ = "custom_config.json"
    value: str = "test"


class TestFileSettingsCreate:
    """Tests for FileSettings.create() method."""

    def test_create_new_settings(self, tmp_path: Path) -> None:
        """Test creating new settings file."""
        settings = SimpleSettings.create(tmp_path)

        assert settings.name == "default"
        assert settings.count == 0
        assert settings.enabled is True
        assert (tmp_path / "settings.json").exists()

    def test_create_creates_directory(self, tmp_path: Path) -> None:
        """Test that create() creates parent directories."""
        nested_dir = tmp_path / "nested" / "deep" / "config"
        settings = SimpleSettings.create(nested_dir)

        assert (nested_dir / "settings.json").exists()
        assert settings.name == "default"

    def test_create_raises_if_exists(self, tmp_path: Path) -> None:
        """Test that create() raises SettingsExistsError if file exists."""
        SimpleSettings.create(tmp_path)

        with pytest.raises(SettingsExistsError) as exc_info:
            SimpleSettings.create(tmp_path)

        assert "already exists" in str(exc_info.value)

    def test_create_exists_ok(self, tmp_path: Path) -> None:
        """Test create() with exists_ok=True overwrites existing file."""
        settings1 = SimpleSettings.create(tmp_path)
        settings1.name = "modified"
        settings1.save()

        settings2 = SimpleSettings.create(tmp_path, exists_ok=True)

        assert settings2.name == "default"  # Reset to default

    def test_create_custom_filename(self, tmp_path: Path) -> None:
        """Test create() with custom filename."""
        CustomFilenameSettings.create(tmp_path)

        assert (tmp_path / "custom_config.json").exists()
        assert not (tmp_path / "settings.json").exists()


class TestFileSettingsLoad:
    """Tests for FileSettings.load() method."""

    def test_load_existing_settings(self, tmp_path: Path) -> None:
        """Test loading existing settings file."""
        # Create settings file manually
        settings_data = {"name": "loaded", "count": 42, "enabled": False}
        (tmp_path / "settings.json").write_text(
            json.dumps(settings_data), encoding="utf8"
        )

        settings = SimpleSettings.load(tmp_path)

        assert settings.name == "loaded"
        assert settings.count == 42
        assert settings.enabled is False

    def test_load_raises_if_not_found(self, tmp_path: Path) -> None:
        """Test that load() raises SettingsNotFoundError if file doesn't exist."""
        with pytest.raises(SettingsNotFoundError) as exc_info:
            SimpleSettings.load(tmp_path)

        assert "not found" in str(exc_info.value)

    def test_load_create_if_missing(self, tmp_path: Path) -> None:
        """Test load() with create_if_missing=True."""
        settings = SimpleSettings.load(tmp_path, create_if_missing=True)

        assert settings.name == "default"
        assert (tmp_path / "settings.json").exists()

    def test_load_invalid_json_raises_value_error(self, tmp_path: Path) -> None:
        """Test that load() raises ValueError for invalid JSON."""
        (tmp_path / "settings.json").write_text("invalid json", encoding="utf8")

        with pytest.raises(ValueError) as exc_info:
            SimpleSettings.load(tmp_path)

        assert "Invalid settings data" in str(exc_info.value)

    def test_load_invalid_data_raises_value_error(self, tmp_path: Path) -> None:
        """Test that load() raises ValueError for invalid data types."""
        settings_data = {"name": "test", "count": "not a number", "enabled": True}
        (tmp_path / "settings.json").write_text(
            json.dumps(settings_data), encoding="utf8"
        )

        with pytest.raises(ValueError) as exc_info:
            SimpleSettings.load(tmp_path)

        assert "Invalid settings data" in str(exc_info.value)

    def test_load_custom_filename(self, tmp_path: Path) -> None:
        """Test load() with custom filename."""
        CustomFilenameSettings.create(tmp_path)
        settings = CustomFilenameSettings.load(tmp_path)
        assert settings.value == "test"
        assert (tmp_path / "custom_config.json").exists()


class TestFileSettingsSave:
    """Tests for FileSettings.save() method."""

    def test_save_updates_file(self, tmp_path: Path) -> None:
        """Test that save() updates the file."""
        settings = SimpleSettings.create(tmp_path)
        settings.name = "updated"
        settings.count = 100
        settings.save()

        # Reload and verify
        loaded = SimpleSettings.load(tmp_path)
        assert loaded.name == "updated"
        assert loaded.count == 100

    def test_save_creates_directory(self, tmp_path: Path) -> None:
        """Test that save() creates parent directories if they don't exist."""
        settings = SimpleSettings.create(tmp_path)

        # Simulate directory being deleted
        new_dir = tmp_path / "new_location"
        settings._settings_dir = new_dir
        settings.save()

        assert (new_dir / "settings.json").exists()

    def test_save_preserves_formatting(self, tmp_path: Path) -> None:
        """Test that save() creates properly formatted JSON."""
        SimpleSettings.create(tmp_path)
        content = (tmp_path / "settings.json").read_text(encoding="utf8")

        # Should be indented (pretty-printed)
        assert "\n" in content
        assert "  " in content  # 2-space indent

    def test_save_raises_oserror_on_write_failure(self, tmp_path: Path) -> None:
        """Test that save() raises OSError with custom message on write failure."""
        settings = SimpleSettings.create(tmp_path)

        with patch.object(Path, "write_text", side_effect=PermissionError("Access denied")):
            with pytest.raises(OSError) as exc_info:
                settings.save()

            assert "Failed to save settings to" in str(exc_info.value)


class TestFileSettingsExists:
    """Tests for FileSettings.exists() method."""

    def test_exists_returns_true_when_file_exists(self, tmp_path: Path) -> None:
        """Test exists() returns True when settings file exists."""
        SimpleSettings.create(tmp_path)

        assert SimpleSettings.exists(tmp_path) is True

    def test_exists_returns_false_when_file_missing(self, tmp_path: Path) -> None:
        """Test exists() returns False when settings file is missing."""
        assert SimpleSettings.exists(tmp_path) is False

    def test_exists_with_custom_filename(self, tmp_path: Path) -> None:
        """Test exists() with custom filename."""
        CustomFilenameSettings.create(tmp_path)

        assert CustomFilenameSettings.exists(tmp_path) is True
        assert SimpleSettings.exists(tmp_path) is False


class TestValidateAssignment:
    """Tests for validate_assignment behavior."""

    def test_validate_assignment_on_change(self, tmp_path: Path) -> None:
        """Test that validation runs on attribute assignment."""
        settings = SimpleSettings.create(tmp_path)

        with pytest.raises(ValidationError):
            settings.count = "not a number"  # type: ignore

    def test_valid_assignment_works(self, tmp_path: Path) -> None:
        """Test that valid assignments work correctly."""
        settings = SimpleSettings.create(tmp_path)
        settings.count = 999

        assert settings.count == 999


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_settings_not_found_is_settings_error(self) -> None:
        """Test that SettingsNotFoundError inherits from SettingsError."""
        assert issubclass(SettingsNotFoundError, SettingsError)

    def test_settings_exists_is_settings_error(self) -> None:
        """Test that SettingsExistsError inherits from SettingsError."""
        assert issubclass(SettingsExistsError, SettingsError)

    def test_catch_all_with_settings_error(self, tmp_path: Path) -> None:
        """Test catching all errors with SettingsError."""
        with pytest.raises(SettingsError):
            SimpleSettings.load(tmp_path)

        SimpleSettings.create(tmp_path)
        with pytest.raises(SettingsError):
            SimpleSettings.create(tmp_path)


class TestBaseSettings:
    """Tests for BaseSettings class."""

    def test_base_settings_validate_assignment(self) -> None:
        """Test that BaseSettings has validate_assignment enabled."""

        class TestSettings(BaseSettings):
            value: int = 0

        settings = TestSettings()
        with pytest.raises(ValidationError):
            settings.value = "not an int"  # type: ignore


class TestStringPaths:
    """Tests for string path arguments."""

    def test_exists_with_string_path(self, tmp_path: Path) -> None:
        """Test exists() accepts string path."""
        SimpleSettings.create(tmp_path)
        assert SimpleSettings.exists(str(tmp_path)) is True

    def test_exists_with_string_path_not_found(self, tmp_path: Path) -> None:
        """Test exists() accepts string path when file doesn't exist."""
        assert SimpleSettings.exists(str(tmp_path)) is False

    def test_create_with_string_path(self, tmp_path: Path) -> None:
        """Test create() accepts string path."""
        settings = SimpleSettings.create(str(tmp_path))
        assert settings.name == "default"
        assert (tmp_path / "settings.json").exists()

    def test_load_with_string_path(self, tmp_path: Path) -> None:
        """Test load() accepts string path."""
        SimpleSettings.create(tmp_path)
        settings = SimpleSettings.load(str(tmp_path))
        assert settings.name == "default"


class TestEdgeCases:
    """Tests for edge cases."""

    def test_load_empty_json_uses_defaults(self, tmp_path: Path) -> None:
        """Test that loading empty JSON {} uses default values."""
        (tmp_path / "settings.json").write_text("{}", encoding="utf8")
        settings = SimpleSettings.load(tmp_path)
        assert settings.name == "default"
        assert settings.count == 0
        assert settings.enabled is True

    def test_load_with_extra_fields_raises_error(self, tmp_path: Path) -> None:
        """Test that extra fields in JSON raise ValueError."""
        settings_data = {
            "name": "test",
            "count": 1,
            "enabled": True,
            "unknown_field": "should cause error",
        }
        (tmp_path / "settings.json").write_text(
            json.dumps(settings_data), encoding="utf8"
        )
        with pytest.raises(ValueError) as exc_info:
            SimpleSettings.load(tmp_path)
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_unicode_values(self, tmp_path: Path) -> None:
        """Test that unicode values are handled correctly."""
        settings = SimpleSettings.create(tmp_path)
        settings.name = "Привіт світ 🌍"
        settings.save()

        loaded = SimpleSettings.load(tmp_path)
        assert loaded.name == "Привіт світ 🌍"

    def test_settings_dir_is_resolved(self, tmp_path: Path) -> None:
        """Test that _settings_dir contains resolved path after load."""
        SimpleSettings.create(tmp_path)
        settings = SimpleSettings.load(tmp_path)
        assert settings._settings_dir == tmp_path.resolve()


class TestModuleExports:
    """Tests for module exports."""

    def test_all_exports_are_accessible(self) -> None:
        """Test that all items in __all__ are accessible from the module."""
        expected_exports = [
            "BaseSettings",
            "FileSettings",
            "SettingsError",
            "SettingsNotFoundError",
            "SettingsExistsError",
        ]
        for name in expected_exports:
            assert hasattr(pydantic_file_settings, name)
            assert name in pydantic_file_settings.__all__

    def test_all_matches_actual_exports(self) -> None:
        """Test that __all__ contains exactly the expected exports."""
        expected = {
            "BaseSettings",
            "FileSettings",
            "SettingsError",
            "SettingsNotFoundError",
            "SettingsExistsError",
        }
        assert set(pydantic_file_settings.__all__) == expected


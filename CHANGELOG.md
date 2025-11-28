# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Custom exceptions: `SettingsError`, `SettingsNotFoundError`, `SettingsExistsError`
- Auto-creation of parent directories in `save()` method
- `py.typed` marker for PEP 561 compliance (type hint support)
- Comprehensive test suite for `FileSettings`
- Coverage configuration

### Changed

- **BREAKING:** Minimum Python version bumped to 3.11
- Updated to Pydantic v2 syntax (`model_config = ConfigDict(...)` instead of `class Config`)
- Modernized type hints
- Updated `pydantic-settings` dependency to 2.8.1
- Migrated from rye to uv for dependency management
- Improved documentation and examples in README

### Removed

- Auto-reload feature
- Author acknowledgement from README

## [0.0.1] - 2024-07-04

### Added

- Initial release
- `FileSettings` base class for managing application settings
- JSON file-based storage for settings
- `create()` method to create new settings files
- `load()` method to load existing settings
- `save()` method to persist settings changes
- `exists()` method to check if settings file exists
- Support for custom filenames
- Type-safe settings with Pydantic validation

[Unreleased]: https://github.com/ruslan-rv-ua/pydantic-file-settings/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/ruslan-rv-ua/pydantic-file-settings/releases/tag/v0.0.1

# Pydantic File Settings

[![PyPI version](https://badge.fury.io/py/pydantic-file-settings.svg)](https://badge.fury.io/py/pydantic-file-settings)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/pydantic-file-settings.svg)](https://pypi.org/project/pydantic-file-settings/)

Manage your application settings with Pydantic models, storing them in a JSON file.

## Features

- 🚀 Easy to use: Extend from `FileSettings` and you're good to go!
- 🔒 Type-safe: Leverage Pydantic's powerful type checking and validation
- 💾 File-based: Store your settings in a JSON file for easy management
- 💪 Flexible: Create, load, and save settings with ease

## Installation

```bash
pip install pydantic-file-settings
```

## Quick Start

Here's a simple example to get you started:

```python
from pydantic_file_settings import FileSettings
from pydantic import Field

class MyAppSettings(FileSettings):
    app_name: str = "My Awesome App"
    debug_mode: bool = False
    max_connections: int = Field(default=100, ge=1, le=1000)

# Create settings file with default values
settings = MyAppSettings.create("./config")

# Load existing settings
settings = MyAppSettings.load("./config")

# Modify and save settings
settings.debug_mode = True
settings.save()
```

## Usage

### Defining Your Settings

Inherit from `FileSettings` and define your settings as class attributes:

```python
from pydantic_file_settings import FileSettings
from pydantic import Field

class MyAppSettings(FileSettings):
    app_name: str
    debug_mode: bool = False
    max_connections: int = Field(default=100, ge=1, le=1000)
```

### Creating Settings

To create a new settings file:

```python
# Create settings (raises SettingsExistsError if file exists)
settings = MyAppSettings.create("./config")

# Create settings, overwriting if file already exists
settings = MyAppSettings.create("./config", exists_ok=True)
```

### Loading Settings

To load existing settings:

```python
# Load settings (raises SettingsNotFoundError if file doesn't exist)
settings = MyAppSettings.load("./config")

# Load settings, creating file with defaults if it doesn't exist
settings = MyAppSettings.load("./config", create_if_missing=True)
```

### Saving Settings

After modifying settings, save them back to the file:

```python
settings.app_name = "New App Name"
settings.save()
```

### Checking if Settings Exist

You can check if a settings file exists:

```python
if MyAppSettings.exists("./config"):
    print("Settings file found!")
```

## Advanced Usage

### Custom Filename

By default, settings are stored in `settings.json`. You can customize the filename:

```python
class MyAppSettings(FileSettings):
    __FILENAME__ = "app_config.json"
    
    app_name: str = "My App"
```

### Environment Variables

Pydantic File Settings supports loading values from environment variables. Use the `validation_alias` parameter in `Field`:

```python
class MyAppSettings(FileSettings):
    api_key: str = Field(default="", validation_alias="MY_APP_API_KEY")
```

### Validation

Leverage Pydantic's validation features:

```python
from pydantic import Field, field_validator

class MyAppSettings(FileSettings):
    port: int = Field(default=8000, ge=1024, le=65535)
    
    @field_validator("port")
    @classmethod
    def port_must_be_even(cls, v: int) -> int:
        if v % 2 != 0:
            raise ValueError("Port must be an even number")
        return v
```

### BaseSettings

The library also exports `BaseSettings` with `validate_assignment=True` enabled, useful when you need validation without file storage:

```python
from pydantic_file_settings import BaseSettings

class RuntimeConfig(BaseSettings):
    debug: bool = False
```

## Exception Reference

| Exception | Raised by | When |
|-----------|-----------|------|
| `SettingsError` | — | Base exception for all settings errors |
| `SettingsNotFoundError` | `load()` | Settings file doesn't exist |
| `SettingsExistsError` | `create()` | Settings file already exists (when `exists_ok=False`) |
| `ValueError` | `load()` | Settings file contains invalid JSON or data |
| `OSError` | `save()` | Failed to write settings file (e.g., permission denied) |

### Error Handling Example

```python
from pydantic_file_settings import (
    FileSettings,
    SettingsError,
    SettingsNotFoundError,
    SettingsExistsError,
)

# Handling load errors
try:
    settings = MyAppSettings.load("./config")
except SettingsNotFoundError:
    print("Settings file not found!")
except ValueError:
    print("Invalid settings data!")

# Handling create errors
try:
    settings = MyAppSettings.create("./config")
except SettingsExistsError:
    print("Settings file already exists!")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Pydantic](https://docs.pydantic.dev/) for the awesome data validation library

---

Made with ❤️ by Ruslan Iskov
# Pydantic File Settings

[![PyPI version](https://badge.fury.io/py/pydantic-file-settings.svg)](https://badge.fury.io/py/pydantic-file-settings)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/pydantic-file-settings.svg)](https://pypi.org/project/pydantic-file-settings/)

Manage your application settings with Pydantic models, storing them in a JSON file.

## Features

- 🚀 Easy to use: Extend from `FileSettings` and you're good to go!
- 🔒 Type-safe: Leverage Pydantic's powerful type checking and validation
- 💾 File-based: Store your settings in a JSON file for easy management
- 🔄 Auto-reload: Automatically load settings from file
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

# Create settings
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
    api_key: str = Field(default="", validation_alias="MY_APP_API_KEY")
```

### Creating Settings

To create a new settings file:

```python
settings = MyAppSettings.create("./config")
```

### Loading Settings

To load existing settings:

```python
settings = MyAppSettings.load("./config")
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

### Custom Exceptions

The library provides custom exceptions for better error handling:

```python
from pydantic_file_settings import (
    FileSettings,
    SettingsError,
    SettingsNotFoundError,
    SettingsExistsError,
)

try:
    settings = MyAppSettings.load("./config")
except SettingsNotFoundError:
    print("Settings file not found!")
except SettingsExistsError:
    print("Settings file already exists!")
except SettingsError:
    print("General settings error!")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Pydantic](https://pydantic-docs.helpmanual.io/) for the awesome data validation library
- [Ruslan Iskov](https://github.com/ruslan-rv-ua) for creating and maintaining this project

---

Made with ❤️ by Ruslan Iskov
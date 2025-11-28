"""Manage your application settings storing them in JSON file."""

from pathlib import Path
from typing import Type, TypeVar, Union

import pydantic_settings
from pydantic import PrivateAttr, ValidationError


T = TypeVar("T", bound="FileSettings")


class BaseSettings(pydantic_settings.BaseSettings):
    class Config:
        validate_assignment = True


class FileSettings(BaseSettings):
    """
    A class for managing application settings stored in a JSON file.

    This class extends BaseSettings from pydantic_settings and provides
    methods for creating, loading, and saving settings to a JSON file.

    Attributes:
        __FILENAME__ (str): The name of the JSON file to store settings.
    """

    _settings_dir: Path = PrivateAttr()

    __FILENAME__: str = "settings.json"

    @classmethod
    def exists(cls, settings_dir: Union[str, Path]) -> bool:
        """
        Check if the settings file exists in the specified directory.

        Args:
            settings_dir (Union[str, Path]): The directory to check for the settings file.

        Returns:
            bool: True if the settings file exists, False otherwise.
        """
        return (Path(settings_dir).resolve() / cls.__FILENAME__).exists()

    @classmethod
    def create(
        cls: Type[T], settings_dir: Union[str, Path], exists_ok: bool = False
    ) -> T:
        """
        Create a new settings file in the specified directory.

        Args:
            settings_dir (Union[str, Path]): The directory to create the settings file in.
            exists_ok (bool, optional): If True, don't raise an error if the file already exists. Defaults to False.

        Returns:
            T: An instance of the FileSettings class.

        Raises:
            FileExistsError: If the settings file already exists and exists_ok is False.
        """
        settings_dir = Path(settings_dir).resolve()
        if not exists_ok and cls.exists(settings_dir):
            raise FileExistsError(
                f"`{cls.__FILENAME__}` already exists in `{settings_dir}`"
            )
        settings = cls()
        settings._settings_dir = settings_dir
        settings.save()
        return settings

    @classmethod
    def load(
        cls: Type[T], settings_dir: Union[str, Path], create_if_missing: bool = False
    ) -> T:
        """
        Load settings from a JSON file in the specified directory.

        Args:
            settings_dir (Union[str, Path]): The directory to load the settings file from.
            create_if_missing (bool, optional): If True, create a new settings file if it doesn't exist. Defaults to False.

        Returns:
            T: An instance of the FileSettings class with loaded settings.

        Raises:
            FileNotFoundError: If the settings file doesn't exist and create_if_missing is False.
            ValueError: If the settings file contains invalid data.
        """
        settings_dir = Path(settings_dir).resolve()
        if not cls.exists(settings_dir):
            if create_if_missing:
                return cls.create(settings_dir)
            raise FileNotFoundError(
                f"`{cls.__FILENAME__}` not found in `{settings_dir}`"
            )

        json_data = (settings_dir / cls.__FILENAME__).read_text(encoding="utf8")
        try:
            settings_object = cls.model_validate_json(json_data)
        except ValidationError as e:
            raise ValueError(f"Invalid settings data: {e}")
        settings_object._settings_dir = settings_dir
        return settings_object

    def save(self) -> None:
        """
        Save the current settings to the JSON file.

        Raises:
            IOError: If there's an error while saving the settings file.
        """
        file_path = self._settings_dir / self.__FILENAME__
        try:
            file_path.write_text(self.model_dump_json(indent=2), encoding="utf8")
        except IOError as e:
            raise IOError(f"Failed to save settings to {file_path}: {e}")

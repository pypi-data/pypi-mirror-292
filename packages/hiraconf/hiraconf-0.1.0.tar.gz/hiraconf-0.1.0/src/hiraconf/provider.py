import os
import tomllib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml


class Provider(ABC):
    @abstractmethod
    def load(self) -> dict[str, Any]: ...


class TomlFileProvider(Provider):
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

    def load(self) -> dict[str, Any]:
        if self.filepath.exists():
            with self.filepath.open("rb") as f:
                data = tomllib.load(f)
            return data
        raise FileNotFoundError(f"File does not exist: {self.filepath}")


class TomlStringProvider(Provider):
    def __init__(self, toml_string: str) -> None:
        self.toml_string = toml_string

    def load(self) -> dict[str, Any]:
        return tomllib.loads(self.toml_string)


class YamlFileProvider(Provider):
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

    def load(self) -> dict[str, Any]:
        if self.filepath.exists():
            with self.filepath.open("r") as f:
                data = yaml.safe_load(f)
            return data
        raise FileNotFoundError(f"File does not exist: {self.filepath}")


class YamlStringProvider(Provider):
    def __init__(self, yaml_string: str) -> None:
        self.yaml_string = yaml_string

    def load(self) -> dict[str, Any]:
        return yaml.safe_load(self.yaml_string)


class EnvPrefixProvider(Provider):
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def load(self) -> dict[str, Any]:
        tmp: dict[str, Any] = {}
        for key, value in os.environ.items():
            if key.startswith(self.prefix.upper()):
                tmp[key.removeprefix(self.prefix).lower()] = value
        return tmp

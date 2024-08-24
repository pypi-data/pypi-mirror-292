from typing import Any, Self

from pydantic import BaseModel

from hiraconf.provider import Provider


class Parser:
    def __init__(self) -> None:
        self.data: dict[str, Any] = {}

    def merge(self, provider: Provider) -> Self:
        if self.data:
            self._merge(first=self.data, second=provider.load())
        else:
            self.data = provider.load()
        return self

    def _merge(self, first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
        for key in second:
            if key in first:
                if isinstance(first[key], dict) and isinstance(second[key], dict):
                    self._merge(first[key], second[key])
                elif first[key] != second[key]:
                    first[key] = second[key]
            else:
                first[key] = second[key]
        return first

    def join(self, provider: Provider) -> Self:
        if self.data:
            self._join(first=self.data, second=provider.load())
        else:
            self.data = provider.load()
        return self

    def _join(self, first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
        for key in second:
            if key in first:
                if isinstance(first[key], dict) and isinstance(second[key], dict):
                    self._join(first[key], second[key])
                elif first[key] != second[key]:
                    continue
            else:
                first[key] = second[key]
        return first

    def extract(self, config: type[BaseModel]) -> BaseModel:
        return config(**self.data)

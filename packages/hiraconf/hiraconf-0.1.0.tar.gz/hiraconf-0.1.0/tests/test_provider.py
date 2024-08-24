import os
from pathlib import Path

from hiraconf.provider import (
    EnvPrefixProvider,
    TomlFileProvider,
    TomlStringProvider,
    YamlFileProvider,
    YamlStringProvider,
)

testfiles = Path(__file__).parent / "testfiles"


def test_environment_prefix_provider() -> None:
    os.environ["HIRACONF_DEBUG"] = "True"
    os.environ["HIRACONF_VERSION"] = "1.0.0"

    loaded = EnvPrefixProvider("HIRACONF_").load()

    assert loaded == {"debug": "True", "version": "1.0.0"}


def test_toml_string_provider() -> None:
    toml_string = """[settings]
    debug = true
    version = "1.0.0"
    """
    loaded = TomlStringProvider(toml_string=toml_string).load()

    assert loaded == {"settings": {"debug": True, "version": "1.0.0"}}


def test_yaml_string_provider() -> None:
    yaml_string = """settings:
      debug: true
      version: 1.0.0
    """

    loaded = YamlStringProvider(yaml_string=yaml_string).load()

    assert loaded == {"settings": {"debug": True, "version": "1.0.0"}}


def test_toml_file_provider() -> None:
    loaded = TomlFileProvider(filepath=Path(testfiles, "second.toml")).load()

    assert loaded == {"settings": {"debug": True, "version": "1.1.0", "new": 10}}


def test_yaml_file_provider() -> None:
    loaded = YamlFileProvider(filepath=Path(testfiles, "first.yaml")).load()

    assert loaded == {"settings": {"debug": True, "version": "1.0.0"}}

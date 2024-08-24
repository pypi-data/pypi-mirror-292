import os

from hiraconf.parser import Parser
from hiraconf.provider import TomlStringProvider, YamlStringProvider

os.environ["HIRACONF_DEBUG"] = "True"
os.environ["HIRACONF_VERSION"] = "1.0.0"

yaml_string = """settings:
  debug: true
  version: 1.0.0
"""

toml_string = """[settings]
debug = true
version = "1.1.0"
new = 10
"""


def test_first_merge() -> None:
    data = Parser().merge(YamlStringProvider(yaml_string=yaml_string)).data

    assert data == {"settings": {"debug": True, "version": "1.0.0"}}


def test_second_merge() -> None:
    data = (
        Parser().merge(YamlStringProvider(yaml_string=yaml_string)).merge(TomlStringProvider(toml_string=toml_string))
    ).data

    assert data == {"settings": {"debug": True, "version": "1.1.0", "new": 10}}


def test_first_join() -> None:
    data = Parser().join(YamlStringProvider(yaml_string=yaml_string)).data

    assert data == {"settings": {"debug": True, "version": "1.0.0"}}


def test_second_join() -> None:
    data = (
        Parser().join(YamlStringProvider(yaml_string=yaml_string)).join(TomlStringProvider(toml_string=toml_string))
    ).data

    assert data == {"settings": {"debug": True, "version": "1.0.0", "new": 10}}

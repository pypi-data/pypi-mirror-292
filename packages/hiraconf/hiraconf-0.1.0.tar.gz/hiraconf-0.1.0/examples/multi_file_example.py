import os
from pathlib import Path

from hiraconf.parser import Parser
from hiraconf.provider import EnvPrefixProvider, TomlFileProvider, YamlFileProvider

"""
These are all config files and Envvars that need to be merged together
"""

default_settings = Path(__file__).parent / "configs" / "default.yaml"
global_settings = Path(__file__).parent / "configs" / "global.yaml"
workspace_settings = Path(__file__).parent / "configs" / "workspace.toml"
os.environ["HIRACONF_ENV_VALUE"] = "100"

"""
This will parse each file and overwrite previous values and add new ones
"""

config = (
    Parser()
    .merge(YamlFileProvider(default_settings))
    .merge(YamlFileProvider(global_settings))
    .merge(TomlFileProvider(workspace_settings))
    .merge(EnvPrefixProvider("HIRACONF_"))
)

print(config.data)
# >>> {'settings': {'value': 3, 'default': True, 'global': True, 'workspace': True}, 'env_value': '100'}

"""
This will parse each file and NOT overwrite previous values, but add new ones
"""


config = (
    Parser()
    .join(YamlFileProvider(default_settings))
    .join(YamlFileProvider(global_settings))
    .join(TomlFileProvider(workspace_settings))
    .join(EnvPrefixProvider("HIRACONF_"))
)

print(config.data)
# >>> {'settings': {'value': 1, 'default': True, 'global': True, 'workspace': True}, 'env_value': '100'}

# HiraConf

A hierarchical parser for configurations, allowing to merge or join configurations from multiple sources.

# Example

Using Pydantic for extracting the parsed configuration in this example, which is optional. You can also access the `data` property
to directly access the dictionary.


```python
from pydantic import BaseModel

from hiraconf.parser import Parser
from hiraconf.provider import TomlStringProvider, YamlStringProvider


# Create the BaseModels for validation of configuration
class Settings(BaseModel):
    debug: bool
    version: str
    new: int | None = None


class Config(BaseModel):
    settings: Settings


# Define your config as file, env, string, toml, yaml or any provider that implements the Provider ABC

yaml_settings = """settings:
  debug: true
  version: 1.0.0
  """

parsed_yaml = Parser().merge(YamlStringProvider(yaml_string=yaml_settings)).extract(Config)

print(parsed_yaml)
# >>> settings=Settings(debug=False, version='1.0.0', new=None)

# If you have multiple configs and want to merge those, you can. Like overwriting the debug setting.

toml_settings = """[settings]
debug = false
"""

parsed_merged = (
    Parser()
    .merge(YamlStringProvider(yaml_string=yaml_settings))
    .merge(TomlStringProvider(toml_string=toml_settings))
    .extract(Config)
)

print(parsed_merged)
# >>> settings=Settings(debug=False, version='1.0.0', new=None)

# Or you join it and keep the original value if it exists as is

toml_join_settings = """[settings]
debug = false
new = 10
"""

parsed_joined = (
    Parser()
    .merge(YamlStringProvider(yaml_string=yaml_settings))
    .join(TomlStringProvider(toml_string=toml_join_settings))
    .extract(Config)
)

print(parsed_joined)
# >>> settings=Settings(debug=True, version='1.0.0', new=10)
```

# Provider

You can define your own `Provider` by inheriting from `Provider` and implementing the abstract `load(self) -> dict[str, Any]` method.
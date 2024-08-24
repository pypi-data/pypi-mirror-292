import os
import re

import click
import tomli

DEFAULT_CONFIG_FILES = [
    os.path.join(os.getcwd(), "pyproject.toml"),
]


class CommandConfig:
    """
    The base configuration for a command group configuration.
    """

    pass


class Config:
    """
    The base configuration for the vitaleey CLI configuration in pyproject.toml.

    NOTE: To retrieve the data call `.load()` on the instance.
    """

    dataclass: CommandConfig | None = None

    def __init__(self, main_section: str = "vitaleey"):
        self.main_section = main_section

        self._validate_classname()

    def __call__(self, *args, **kwargs):
        return self.load(*args, **kwargs)

    def get_dataclass(self):
        return self.dataclass

    def _convert_classname(self):
        """
        Get the command group configuration
        """

        return re.sub(r"(?<!^)(?=[A-Z])", "_", self.__class__.__name__).lower()

    def _validate_classname(self):
        if not self._convert_classname().endswith("_config"):
            raise click.ClickException("The class name must end with _config")

    def _filter_command_group(self, config):
        """
        Filter the command group from the configuration
        """

        command_group = self._convert_classname().replace("_config", "")
        return config.get(command_group, {})

    def _parse_dataclass(self, config):
        """
        Parse config to dataclass
        """

        dataclass = self.get_dataclass()
        if dataclass is not None and config:
            return dataclass(**config)
        return config

    def load(self, *args, **kwargs):
        """
        Load the configuration from the pyproject.toml file
        """
        config = {}
        for path in DEFAULT_CONFIG_FILES:
            if os.path.exists(path):
                try:
                    with open(path, "rb") as f:
                        config = tomli.load(f)
                except tomli.TOMLDecodeError as e:
                    click.ClickException(f"Could not load pyproject.toml file: {e}")
                    config = {}
        config = config.get("tool", {}).get(self.main_section, {})
        if not config:
            raise click.ClickException("Could not load the vitaleey configuration")

        config = self._filter_command_group(config)

        return self._parse_dataclass(config)

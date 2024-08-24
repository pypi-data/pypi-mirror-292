from dataclasses import dataclass, field

import click

from vitaleey_cli.env import ENVIRONMENTS, environment_names

from .config import Config

__all__ = ["api_gateway_config"]


@dataclass(frozen=True)
class ApiGatewayDataclass:
    """
    Configuration for an APIGateway environment:
        development, acceptance, production

    Options:
    - endpoint_dir: The directory where the endpoint files are stored
      - enabled: Enable the APIGateway, if not no action will be taken. KrakenD is required to be installed.
    ```
    """

    endpoint_dir: str = "config"
    enabled: bool = True  # Enable the APIGateway


@dataclass(frozen=True)
class EnvironmentDataclass:
    """
    Configuration for all the environments:

    Options:
    - environments: The environments for the APIGateway
    """

    environments: dict[str, ApiGatewayDataclass] = field(default_factory=dict)


class ApiGatewayConfig(Config):
    """
    API Gateway configuration
    """

    @staticmethod
    def _load_env_configs(config):
        """
        Load the environments configurations
        """

        # Get environments
        environments = {}

        config_envs: dict[str, dict] = config.get("env", {})

        # Retrieve environment configurations
        for group, group_config in config_envs.items():
            kwargs = {
                key: value
                for key, value in group_config.items()
                if key in ApiGatewayDataclass.__annotations__
            }

            # Fill missing keys with global_config
            for key in ApiGatewayDataclass.__annotations__:
                if not kwargs.get(key) and config.get(key):
                    kwargs[key] = config.get(key)
            environments[group] = ApiGatewayDataclass(**kwargs)
        return EnvironmentDataclass(environments=environments)

    def load(self, **kwargs):
        """
        Load the configuration based on the environment
        """

        environment = kwargs.get("environment")
        if environment not in ENVIRONMENTS:
            raise click.UsageError(f"Invalid environment, choose from: {ENVIRONMENTS}")

        click.secho(
            f"Loading configuration for {environment_names.get_group(environment)} environment",
            bold=True,
        )

        config = super().load(**kwargs)
        env_configs = self._load_env_configs(config)

        environment_options = environment_names.get_group_options(environment)

        for env in environment_options:
            env_config = env_configs.environments.get(env)
            if env_config:
                return env_config


api_gateway_config = ApiGatewayConfig()

import os
from dataclasses import dataclass

from .config import CommandConfig, Config

__all__ = ["application_config"]

DEFAULT_PYTHON_REGISTRY = "registry.gitlab.com/vitaleey"
DEFAULT_DOCKER_REGISTRY = "registry.gitlab.com/vitaleey"


@dataclass(frozen=True)
class ApplicationDataclass(CommandConfig):
    """
    Configuration for the application

    Options:
    - registry: The registry to publish the application to
    """

    python_registry: str = DEFAULT_PYTHON_REGISTRY
    docker_registry: str = DEFAULT_DOCKER_REGISTRY
    docker_image_name: str = ""


class ApplicationConfig(Config):
    """
    Application configuration
    """

    dataclass = ApplicationDataclass


application_config = ApplicationConfig()

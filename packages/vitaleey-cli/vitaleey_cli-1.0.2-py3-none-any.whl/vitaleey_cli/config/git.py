import os
from dataclasses import dataclass

from .config import CommandConfig, Config

__all__ = ["gitlab_config"]


@dataclass(frozen=True)
class GitlabDataclass(CommandConfig):
    """
    Configuration for Git

    Options:
    - branch: The target branch
    - project_id: The project ID
    """

    branch: str = ""
    project_id: str = ""


class GitlabConfig(Config):
    """
    Git configuration
    """

    dataclass = GitlabDataclass


gitlab_config = GitlabConfig()

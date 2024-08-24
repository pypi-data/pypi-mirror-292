import click

from .docker import group as docker_group
from .python import group as python_group


@click.group(help="Application helper commands")
def group():
    pass


group.add_command(docker_group, name="docker")
group.add_command(python_group, name="python")

import os
import sys
import click
from .__about__ import __version__
from .client import Primitive
from .auth.commands import config_command, whoami_command
from .files.commands import cli as file_commands
from .hardware.commands import cli as hardware_commands
from .lint.commands import cli as lint_commands
from .agent.commands import cli as agent_commands
from .git.commands import cli as git_commands


@click.group()
@click.option(
    "--host",
    required=False,
    default=lambda: os.environ.get("PRIMITIVE_HOST", "api.primitive.tech"),
    show_default="api.primitive.tech",
    help="Environment of Primitive API",
)
@click.option(
    "--yes", is_flag=True, show_default=True, default=False, help="Skip interactions."
)
@click.option(
    "--debug", is_flag=True, show_default=True, default=False, help="Enable debug mode."
)
@click.option(
    "--json",
    is_flag=True,
    show_default=True,
    default=False,
    help="Turn all outputs into JSON.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Verbosity of output levels.",
)
@click.version_option(__version__)
@click.pass_context
def cli(context, host, yes, debug, json, verbose):
    """primitive - a CLI tool for https://primitive.design"""
    context.ensure_object(dict)
    context.obj["YES"] = yes
    context.obj["DEBUG"] = debug
    context.obj["JSON"] = json
    context.obj["VERBOSE"] = verbose
    context.obj["HOST"] = host
    if "config" not in sys.argv:
        context.obj["PRIMITIVE"] = Primitive(host=host, DEBUG=debug, JSON=json)


cli.add_command(config_command, "config")
cli.add_command(whoami_command, "whoami")
cli.add_command(file_commands, "files")
cli.add_command(hardware_commands, "hardware")
cli.add_command(lint_commands, "lint")
cli.add_command(agent_commands, "agent")
cli.add_command(git_commands, "git")

if __name__ == "__main__":
    cli(obj={})

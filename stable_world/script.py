"""
This is a command
"""
from __future__ import print_function
import click
from stable_world import __version__ as sw_version


@click.group(invoke_without_command=True)
@click.option('--debug/--no-debug', default=False)
@click.version_option(sw_version)
# @click.help_option('-h/--help')
@click.pass_context
def main(ctx, debug):
    """Simple program that greets NAME for a total of COUNT times."""
    print("ctx", ctx.invoked_subcommand)


@main.command()
def use():
    """Simple program that greets NAME for a total of COUNT times."""


@main.command()
def success():
    """Simple program that greets NAME for a total of COUNT times."""


@main.command()
def diff():
    """Simple program that greets NAME for a total of COUNT times."""


@main.command()
def pin():
    """Simple program that greets NAME for a total of COUNT times."""


@main.command()
def unpin():
    """Simple program that greets NAME for a total of COUNT times."""


if __name__ == '__main__':
    main()

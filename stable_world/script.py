"""
This is a command
"""
from __future__ import print_function
import os
import click
from stable_world import __version__ as sw_version
from .config import config_filename, update_config
from .setup_user import setup_user
from . import utils


@click.group(invoke_without_command=True)
@click.option('--debug/--no-debug', default=False)
# @click.option('--token', default=os.getenv('STABLE_WORLD_TOKEN'))
@click.version_option(sw_version)
# @click.help_option('-h/--help')
@click.pass_context
def main(ctx, debug):
    """Simple program that greets NAME for a total of COUNT times."""

    ctx.obj = {}

    if ctx.invoked_subcommand:
        return

    print("ctx", ctx)


@main.command()
@click.option('--email', default=os.getenv('STABLE_WORLD_EMAIL'))
@click.option('--password', default=os.getenv('STABLE_WORLD_PASSWORD'))
@click.pass_context
def login(ctx, email, password, token=None):
    "only performs authentication step"
    ctx.obj['client'] = setup_user(email, password, token)
    return


@main.command()
def logout():
    "only performs authentication step"
    update_config(token=None, email=None)
    print(
        '\n\n    '
        'Token removed from %s file.'
        '\n\n' % config_filename
    )
    return


@main.command()
@utils.login_optional
def whoami(client):
    "show who you are logged in as"

    email = client.whoami()
    click.echo('\n\n    Logged in as %s\n\n' % email)
    return


@main.command('space:create')
@utils.email_option
@click.option('-s', '--space')
@utils.login_required
def space_create(client, space):
    "Create a new cache space"
    client.create_space(space)
    return


@main.command('space:url:add')
@click.option('--space', required=True)
@click.option('--url')
@click.option('--type', type=click.Choice(['pypi', 'npm']))
@click.option('--name')
@utils.login_required
def space_url_add(client, space, url, type, name):
    "Create a new cache space"
    client.add_url(name)
    return


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
    main(obj={})

"""
This is a command
"""
from __future__ import print_function
import os
import sys
import click

from stable_world import __version__ as sw_version
from .config import config_filename, update_config
from .interact.setup_user import setup_user
from .interact.setup_space import setup_space
from .interact.setup_urls import setup_urls
from . import utils
from . import errors

original_excepthook = sys.excepthook


def brief_excepthook(exctype, value, tb):

    if issubclass(exctype, errors.UserError):
        print('My Error Information:')
        print('Value:', value)
    else:
        original_excepthook(exctype, value, tb)


@click.group(invoke_without_command=True)
@click.option('--debug/--no-debug', default=False)
@click.option('--hide-traceback/--no-full-traceback', default=False)
@click.version_option(sw_version)
@utils.email_option
@utils.password_option
@utils.token_option
@click.pass_context
def main(ctx, email, password, token, debug, hide_traceback):
    """Simple program that greets NAME for a total of COUNT times."""

    if not hide_traceback:
        sys.excepthook = brief_excepthook

    if ctx.invoked_subcommand:
        return

    client = utils.ensure_login(email, password, token)

    space = setup_space(client)
    setup_urls(client, space)


@main.command()
@click.option('--email', default=os.getenv('STABLE_WORLD_EMAIL'))
@click.option('--password', default=os.getenv('STABLE_WORLD_PASSWORD'))
@click.pass_context
def login(ctx, email, password, token=None):
    "only performs authentication step"
    setup_user(email, password, token)
    return


@main.command()
def logout():
    "only performs authentication step"
    update_config(token=None, email=None)
    click.echo(
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


@main.command('project:create')
@click.option('-p', '--project')
@utils.login_required
def space_create(client, project):
    "Create a new cache space"
    if project:
        client.add_project(project)
        click.echo('    Project %s added!' % project)
    else:
        setup_space(client)
    return


@main.command()
@utils.login_required
def list(client):
    "list all projects you have access to"
    projects = client.projects()
    for project in projects:
        if project['urls']:
            urls = '(%s)' % ', '.join(project['urls'].keys())
        else:
            urls = 'empty'
        click.echo('    %-20s %s' % (project['name'], urls))


@main.command()
@click.option('-p', '--project', required=True)
@utils.login_required
def teardown(client, project):
    "tear down a published project"
    client.delete_project(project)
    click.echo('    Project %s removed' % project)


@main.command('project:url:add')
@click.option('-p', '--project', required=True)
@click.option('--url')
@click.option('--type', type=click.Choice(['pypi', 'npm']))
@click.option('--name')
@utils.login_required
def space_url_add(client, project, url, type, name):
    "Add a cache to the project"
    if url and type and name:
        client.add_url(project, url, type, name)
        click.echo('    Caching url %s as %s' % (url, name))
    else:
        setup_urls(client, project, url, type, name)


@main.command()
@click.option('-t', '--tag', required=True,
    help='Tag all requests with this tag')
@click.option('-p', '--project', required=True,
    help='Project to source from')
@utils.login_required
def use(client, tag, project):
    "Activate and record all usage for a project"
    print(tag, project)


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

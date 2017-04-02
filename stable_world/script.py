"""
This is a command
"""
from __future__ import print_function
import sys

import click

from stable_world import __version__ as sw_version
from .config import config_filename, update_token, config, read_config, make_dirs
from .interact.setup_user import setup_user
from .interact.setup_project import setup_project
from . import utils, errors, output
from .sw_logging import setup_logging
from .use import use_project, unuse_project

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.option('--debug/--no-debug', default=False)
@click.option('--show-traceback/--dont-show-traceback', default=False)
@click.option('--ignore-config/--dont-ignore-config', default=False)
@click.version_option(sw_version)
@utils.email_option
@utils.password_option
@utils.token_option
@utils.dir_option
@click.pass_context
def main(ctx, email, password, token, debug, show_traceback, ignore_config, dir):
    """
    Stable.World cli

    \b
    Environment:
      * STABLE_WORLD_URL - the url of the api server
      * STABLE_WORLD_EMAIL - your account email
      * STABLE_WORLD_TOKEN - token
      * DEBUG - To print all debugging information use DEBUG='*'

    """

    setup_logging()
    if not show_traceback:
        sys.excepthook = errors.brief_excepthook

    make_dirs()

    if not ignore_config:
        read_config()

    if ctx.invoked_subcommand:
        return

    ensure_login = utils.update_config_with_args(utils.ensure_login)
    client = ensure_login(email=email, password=password, token=token)
    setup_project(dir, client)


@main.command()
@utils.email_option
@utils.password_option
@utils.token_option
@utils.update_config_with_args
def login(email, password, token):
    "only performs authentication step"
    setup_user(email, password, token, login_only=True)
    return


@main.command()
@utils.email_option
@utils.password_option
@utils.token_option
@utils.update_config_with_args
def register(email, password, token):
    "only performs authentication step"
    confirm_password = not password
    setup_user(
        email, password, token,
        login_only=False, confirm_password=confirm_password
    )
    return


@main.command()
def logout():
    "expire local token"

    update_token(token=None, email=None)
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
@click.option('-p', '--project', required=True)
@utils.login_required
def project_create(client, project):
    "Create a new project"
    if project:
        info = client.add_project(project)
    else:
        info = setup_project(client)
    output.projects.print_project(info['project'])
    utils.echo_success()
    click.echo('Project %s added!' % info['project']['name'])


@main.command('list')
@utils.login_required
def list_cmd(client):
    "list all projects you have access to"
    projects = client.projects()
    output.projects.print_projects(projects)


@main.command('project')
@utils.project_option(required=True)
@utils.login_required
def project(client, project):
    "show a published project"
    info = client.project(project)
    output.projects.print_project(info['project'])


@main.command('project:destroy')
@utils.project_option(required=True)
@utils.login_required
def project_destroy(client, project):
    "tear down a published project"
    client.delete_project(project)
    utils.echo_success()
    click.echo(' Project %s removed' % project)


@main.command('project:cache:add')
@utils.project_option(required=True)
@click.option('--url')
@click.option('--type')
@click.option('--name', required=True)
@utils.login_required
def project_cache_add(client, project, url, type, name):
    "Add a cache to the project"

    client.add_url(project, url, type, name)

    utils.echo_success()
    click.echo(' Cache %s was added as %s' % (url, name))


@main.command('project:cache:remove')
@utils.project_option(required=True)
@click.option('-n', '--name')
@utils.login_required
def project_cache_remove(client, project, name):
    "Remove a cache from the project"

    info = client.remove_url(project, name)
    utils.echo_success()
    click.echo(' Cache %s (%s) was removed' % (info['url'], name))


@main.command('tag:create')
@utils.project_option(required=True)
@click.option('-n', '--name', required=True)
@utils.login_required
def tag_create(client, project, name):
    "Add a tag to a project"
    client.add_tag(project, name)
    utils.echo_success()
    click.echo("Tag %s added to project %s" % (name, project))


@main.command('tag:list')
@utils.project_option(required=True)
@utils.login_optional
def tag_list(client, project):
    "List tags in a project"
    info = client.project(project)
    output.tags.print_tags(info['tags'][::-1])


@main.command('tag:show')
@utils.project_option(required=True)
@utils.tag_option(required=True)
@utils.login_optional
def tag_show(client, project, tag):
    "List tags in a project"
    info = client.tag_objects(project, tag)
    output.tags.print_objects(info['objects'])


@main.command()
@click.option('-t', '--create-tag', required=True)
@utils.project_option(required=True)
@click.option('--dryrun/--no-dryrun')
@utils.login_required
def use(client, create_tag, project, dryrun):
    "Activate and record all usage for a project"
    use_project(client, create_tag, project, dryrun)


@main.command()
def unuse():
    "Deactivate a project"
    unuse_project()


@main.command()
def using():
    "Deactivate a project"
    using = config.get('using', None)
    if not using:
        click.echo('You are not currently using a project')
        sys.exit(1)
    else:
        click.echo('You are using project "%(project)s", tag "%(tag)s"' % using)

    return


@main.command()
@click.option('-t', '--tags', required=True,
    help='Tag all requests with this tag')
@utils.project_option(required=True)
@utils.login_optional
def diff(client, project, tags):
    """Show the difference between two tags in a project"""
    if ':' in tags:
        first, last = tags.split(':')
    else:
        first, last = tags, None

    diff_result = client.diff(project, first, last)
    output.tags.diff_tags(diff_result)


@main.command()
@utils.project_option(required=True)
@utils.tag_option(required=True)
@utils.login_required
def pin(client, project, tag):
    "Pin a project to a tag."
    client.pin(project, tag)
    utils.echo_success()
    click.echo("Project %s pinned to tag %s" % (project, tag))


@main.command()
@utils.project_option(required=True)
@utils.login_required
def unpin(client, project):
    "Remove pin to tag"
    client.unpin(project)
    utils.echo_success()
    click.echo("Unpinned Project %s" % (project))


@main.command()
@utils.email_option
@utils.password_option
@utils.token_option
@utils.update_config_with_args
def token(email, password, token):
    "Get your authentication token"

    utils.ensure_login(email, password, token, hide_token=False)


@main.command()
@utils.login_optional
def info(client):
    "Fetch environment and server informations"
    output.build_info.build_info(client)


@main.command('setup:custom')
@utils.dir_option
@utils.login_required
def setup_custom(client, dir):
    "Set up new custom project"
    setup_project(dir, client, 'custom')


@main.command('setup:circle')
@utils.dir_option
@utils.login_required
def setup_circle(client, dir):
    "Set up new project on circleci"
    setup_project(dir, client, 'custom')


if __name__ == '__main__':
    main(obj={})

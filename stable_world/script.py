"""
This is a command
"""
from __future__ import print_function
import sys

import click

from stable_world import __version__ as sw_version
from .interact.setup_user import setup_user, setup_project_token
from .interact.setup_project import setup_project
from .interact.use import use_project, unuse_project
from .output import error_output
from .env import env
from .sw_logging import setup_logging
from . import utils, output, application, group

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
    cls=group.StableWorldGroup
)
@click.option(
    '--show-traceback/--dont-show-traceback', default=False,
    help='Show full traceback on a critical error'
)
@click.option(
    '--ignore-config/--dont-ignore-config', default=False,
    help="Don't read the config file from disk"
)
@click.version_option(sw_version)
@application.email_option
@application.password_option
@application.token_option
@utils.dir_option
@application.pass_app
@click.pass_context
def main(ctx, app, show_traceback, ignore_config, dir):
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
    if not show_traceback and not env.DEBUG:
        sys.excepthook = error_output.brief_excepthook(app.cache_dirname)

    if not ignore_config:
        app.read_config()

    app.update_config_from_options()
    app.make_directories()

    if ctx.invoked_subcommand:
        return

    utils.ensure_login(app)
    setup_project(app, dir)


@main.command(category='Authentication')
@application.email_option
@application.password_option
@application.token_option
@application.pass_app
def login(app):
    "only performs authentication step"
    setup_user(app, login_only=True)
    return


@main.command(category='Authentication')
@application.email_option
@application.password_option
@application.token_option
@application.pass_app
def register(app):
    "only performs authentication step"
    confirm_password = not app.password
    setup_user(app, login_only=False, confirm_password=confirm_password)
    return


@main.command()
@application.pass_app
def logout(app):
    "expire local token"

    app.update_netrc(token=None, email=None)
    click.echo(
        '\n\n    '
        'Token removed from %s file.'
        '\n\n' % app.config_filename
    )
    return


@main.command(category='Authentication')
@utils.login_optional
def whoami(app):
    "show who you are logged in as"

    email = app.client.whoami()
    click.echo('\n\n    Logged in as %s\n\n' % email)
    return


@main.command('project:create')
@utils.project_option(required=True)
@utils.login_required
def project_create(app, project):
    "Create a new project"
    if project:
        info = app.client.add_project(project)
    else:
        info = setup_project(app)
    output.projects.print_project(info['project'])
    utils.echo_success()
    click.echo('Project %s added!' % info['project']['name'])


@main.command('project:list')
@utils.login_required
def list_cmd(app):
    "list all projects you have access to"
    projects = app.client.projects()
    output.projects.print_projects(projects)


@main.command('project')
@utils.project_option(required=True)
@utils.login_required
def project(app, project):
    "show a published project"
    info = app.client.project(project)
    output.projects.print_project(info['project'])


@main.command('project:destroy')
@utils.project_option(required=True)
@utils.login_required
def project_destroy(app, project):
    "tear down a published project"
    app.client.delete_project(project)
    utils.echo_success()
    click.echo(' Project %s removed' % project)


@main.command('project:cache:add')
@utils.project_option(required=True)
@click.option('--url', help='The url endpoint to cache')
@click.option('--type', help='type of cache')
@click.option('--name', required=True, help='Give it a name')
@utils.login_required
def project_cache_add(app, project, url, type, name):
    "Add a cache to the project"

    app.client.add_url(project, url, name, type)

    utils.echo_success()
    click.echo(' Cache %s was added as %s' % (url, name))


@main.command('project:cache:remove')
@utils.project_option(required=True)
@click.option('-n', '--name', help='name of cache to remove')
@utils.login_required
def project_cache_remove(app, project, name):
    "Remove a cache from the project"

    info = app.client.remove_url(project, name)
    utils.echo_success()
    click.echo(' Cache %s (%s) was removed' % (info['url'], name))


@main.command('tag:create')
@utils.project_option(required=True)
@click.option('-t', '--tag', required=True, help='name of tag to create')
@utils.login_required
def tag_create(app, project, tag):
    "Add a tag to a project"
    app.client.add_tag(project, tag)
    utils.echo_success()
    click.echo("Tag %s added to project %s" % (tag, project))


@main.command('tag:list')
@utils.project_option(required=True)
@utils.login_optional
def tag_list(app, project):
    "List tags in a project"
    info = app.client.project(project)
    output.tags.print_tags(info['tags'][::-1])


@main.command('tag:show')
@utils.project_option(required=True)
@utils.tag_option(required=True)
@click.option(
    '--full/--exact',
    help='If exact (default) show this tag only, otherwise show all previous tags.'
)
@utils.login_optional
def tag_show(client, project, tag, full):
    "List tags in a project"
    info = client.tag_objects(project, tag, exact=not full)
    output.tags.print_objects(info)


@main.command(category='Build')
@click.option(
    '-t', '--create-tag', required=False,
    help='tag name to create'
)
@utils.project_option(required=True)
@click.option(
    '--dryrun/--no-dryrun',
    help='only print output don\'t create tag or modify config files'
)
@application.email_option
@application.token_option
@application.password_option
@application.pass_app
def use(app, create_tag, project, dryrun):
    "Activate and record all usage for a project"

    if app.token:
        token = app.token
    else:
        token = setup_project_token(app, project)

    use_project(app, create_tag, project, token, dryrun)


@main.command(category='Build')
@application.pass_app
def unuse(app):
    "Deactivate a project"
    unuse_project(app)


@main.command(category='Build')
@application.pass_app
def using(app):
    "Deactivate a project"
    using = app.config.get('using', None)
    if not using:
        click.echo('You are not currently using a project')
        sys.exit(1)
    else:
        click.echo('You are using project "%(project)s", tag "%(tag)s"' % using)

    return


@main.command()
@click.option(
    '-t', '--tags', required=True,
    help='Tag all requests with this tag'
)
@utils.project_option(required=True)
@utils.login_optional
def diff(app, project, tags):
    """Show the difference between two tags in a project"""
    if ':' in tags:
        first, last = tags.split(':')
    else:
        first, last = tags, None

    diff_result = app.client.diff(project, first, last)
    output.tags.diff_tags(diff_result)


@main.command()
@utils.project_option(required=True)
@utils.tag_option(required=True)
@utils.login_required
def pin(app, project, tag):
    "Pin a project to a tag."
    app.client.pin(project, tag)
    utils.echo_success()
    click.echo("Project %s pinned to tag %s" % (project, tag))


@main.command()
@utils.project_option(required=True)
@utils.login_required
def unpin(app, project):
    "Remove pin to tag"
    app.client.unpin(project)
    utils.echo_success()
    click.echo("Unpinned Project %s" % (project))


@main.command(category='Authentication')
@application.email_option
@application.password_option
@utils.project_option(required=True)
@utils.client
def token(app, project):
    "Get your authentication token"

    # Will raise not found exception
    app.client.project(project)

    token = setup_project_token(app, project)
    print("  token:", token)


@main.command()
@utils.login_optional
def info(app):
    "Fetch environment and server informations"
    output.build_info.build_info(app.client)


@main.command('setup')
def setup(app, dir):
    "Set up new project"


@main.command('setup:custom')
@utils.dir_option
@utils.login_required
def setup_custom(app, dir):
    "Set up new custom project"
    setup_project(app, dir, 'custom')


@main.command('setup:circle')
@utils.dir_option
@utils.login_required
def setup_circle(app, dir):
    "Set up new project on circleci"
    setup_project(app, dir, 'circleci')


if __name__ == '__main__':
    main(obj={})

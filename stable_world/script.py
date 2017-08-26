"""
This is a command
"""
from __future__ import print_function
import sys

import click

from stable_world import __version__ as sw_version
from .interact.setup_user import setup_user, setup_bucket_token
from .interact.setup_bucket import setup_bucket
from .interact.use import check_bucket
from .output import error_output
from .env import env
from .sw_logging import setup_logging
from .executors import execute_pip, execute_npm
from . import errors, utils, output, application, group

from .managers.pypi import PyPIManager
from .managers.npm import NPMManager


CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'],
)


@click.group(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
    cls=group.StableWorldGroup
)
@click.option(
    '--show-traceback/--dont-show-traceback', default=False,
    envvar='STABLE_WORLD_SHOW_TRACEBACK',
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

    click.echo("\n  Stable.World CLI Version: ", nl=False)
    click.secho(sw_version, nl=False, bold=True)
    click.secho("")
    click.echo("\n  See other CLI commands with ", nl=False)
    click.secho("stable.world --help", nl=False, fg='magenta', bold=True)
    click.secho("\n")


@main.command(category='Config')
@click.argument('key')
@click.argument('value')
@application.pass_app
def set(app, key, value):
    """Set a config value

    e.g:

    """
    app.write_config(key, value)
    utils.echo_success()
    click.echo('key "{}" was set'.format(key))
    return


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


@main.command('bucket:create')
@click.argument('name')
@utils.login_required
def bucket_create(app, name):
    "Create a new bucket"
    info = app.client.add_bucket(name)
    output.buckets.print_bucket(info['bucket'])
    utils.echo_success()
    click.echo('Bucket "%s" added!' % info['bucket']['name'])


@main.command('bucket:list')
@utils.login_required
def bucket_list(app):
    "list all buckets you have access to"
    buckets = app.client.buckets()
    output.buckets.print_buckets(buckets)


@main.command('bucket')
@utils.bucket_name_argument()
@utils.login_required
def bucket(app, name):
    "show a published bucket"
    info = app.client.bucket(name)
    output.buckets.print_bucket(info['bucket'])


@main.command('bucket:destroy')
@utils.bucket_name_argument()
@utils.login_required
def bucket_destroy(app, name):
    "tear down a published bucket"
    app.client.delete_bucket(name)
    utils.echo_success()
    click.echo(' Bucket %s removed' % bucket)


@main.command('bucket:cache:add')
@utils.bucket_name_argument()
@click.option('--url', help='The url endpoint to cache')
@click.option('--type', help='type of cache')
@click.option('-n', '--cache-name', required=True, help='Give it a name')
@utils.login_required
def bucket_cache_add(app, name, url, type, cache_name):
    "Add a cache to the bucket"

    app.client.add_url(name, url, cache_name, type)

    utils.echo_success()
    click.echo(' Cache %s was added as %s' % (url, cache_name))


@main.command('bucket:cache:remove')
@utils.bucket_name_argument()
@click.option('-n', '--cache-name', help='name of cache to remove')
@utils.login_required
def bucket_cache_remove(app, name, cache_name):
    "Remove a cache from the bucket"

    info = app.client.remove_url(name, cache_name)
    utils.echo_success()
    click.echo(' Cache %s (%s) was removed' % (info['url'], cache_name))


@main.command('bucket:objects')
@click.option(
    '-w', '--since', default=None,
    type=utils.datetime_type,
    help='Show objects after date',
)
@utils.bucket_name_argument()
@utils.login_optional
def bucket_objects(app, name, since=None):
    """Show the objects added to a bucket since a time"""

    if since:
        objects = app.client.objects_since(name, since)
    else:
        objects = app.client.objects(name)

    output.buckets.print_objects(objects)


@main.command('bucket:rollback')
@click.option(
    '-w', '--when', required=True, default=None,
    type=utils.datetime_type,
    help='Rollback after',
)
@utils.bucket_name_argument()
@utils.login_optional
def bucket_rollback(app, name, when):
    """Show the objects added to a bucket since a time"""

    app.client.rollback(name, when)

    utils.echo_success()
    click.echo("Bucket %s rolled back to %s" % (name, when.ctime()))


@main.command('bucket:freeze')
@utils.bucket_name_argument()
@utils.login_required
def bucket_freeze(app, name):
    "Freeze a bucket so it can not be modified"
    app.client.freeze(name)
    utils.echo_success()
    click.echo("Bucket %s frozen" % (name))


@main.command('bucket:unfreeze')
@utils.bucket_name_argument()
@utils.login_required
def bucket_unfreeze(app, name):
    "Unfreeze a bucket so it can be modified"
    app.client.unfreeze(name)
    utils.echo_success()
    click.echo("Unfroze Bucket %s" % (name))


@main.command(category='Authentication')
@application.email_option
@application.password_option
@utils.bucket_option(required=False)
@application.pass_app
def token(app, bucket):
    "Get your authentication token"

    # Will raise not found exception
    if bucket:
        app.client.bucket(bucket)

    token = setup_bucket_token(app, bucket)
    print("  token:", token)


@main.command()
@utils.login_optional
def info(app):
    "Fetch environment and server informations"
    output.build_info.build_info(app.client)


@main.command('ci')
def ci(app, dir):
    "Set up stable.world in your continuous delivery pipline"


@main.command('ci:bash')
@utils.dir_option
@utils.login_required
def ci_bash(app, dir):
    "Set up stable.world in your continuous delivery pipline using bash"
    setup_bucket(app, dir, 'custom')


@main.command('ci:circle')
@utils.dir_option
@utils.login_required
def ci_circle(app, dir):
    "Set up stable.world in your continuous delivery pipline using circleci"
    setup_bucket(app, dir, 'circleci')


@main.command(context_settings=dict(
    ignore_unknown_options=True,
))
@utils.bucket_option(required=True)
@click.argument('pip_args', nargs=-1, type=click.UNPROCESSED)
@utils.login_required
def pip(app, bucket, pip_args):
    """A wrapper around Python's pip"""
    execute_pip(app, bucket, pip_args)


@main.command(context_settings=dict(
    ignore_unknown_options=True,
))
@utils.bucket_option(required=True)
@click.argument('npm_args', nargs=-1, type=click.UNPROCESSED)
@utils.login_required
def npm(app, bucket, npm_args):
    """A wrapper around NodeJS's npm"""
    execute_npm(app, bucket, npm_args)


@main.group(chain=True)
@click.option(
    '--dryrun/--no-dryrun',
    help='only print output don\'t modify config files'
)
@utils.bucket_option(required=True)
def configure(bucket, dryrun):
    "Create user configuration files for commands"
    # Handled in process_configure
    pass


@configure.resultcallback()
@click.pass_context
def process_configure(ctx, managers, bucket, dryrun):

    app = ctx.obj
    token = app.token

    if token:
        try:
            app.client.check_bucket_token(bucket, token)
        except errors.BadAuthorization:
            token = None

    if not token:
        token = setup_bucket_token(app, bucket, use_config_token=False)

    urls = check_bucket(app, bucket, token)

    for Manager in managers:
        mgr = Manager(app.client.site, urls, bucket, token, dryrun)
        mgr.use()


@configure.command('pip')
@click.pass_context
def configure_pip(ctx):
    "set pip user configuration files"
    return PyPIManager


@configure.command('npm')
@application.pass_app
def configure_npm(app):
    "set npm user configuration files"
    return NPMManager


if __name__ == '__main__':
    main(obj={})

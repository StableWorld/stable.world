"""
This is a command
"""
from __future__ import print_function
import sys

import click

from stable_world import __version__ as sw_version
from .interact.setup_user import setup_user, setup_bucket_token
from .interact.setup_bucket import setup_bucket
from .interact.use import use_bucket, unuse_bucket
from .output import error_output
from .env import env
from .sw_logging import setup_logging
from .executors import execute_pip
from . import utils, output, application, group, errors

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
    setup_bucket(app, dir)


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
@utils.bucket_option(required=True)
@utils.login_required
def bucket_create(app, bucket):
    "Create a new bucket"
    if bucket:
        info = app.client.add_bucket(bucket)
    else:
        info = setup_bucket(app)
    output.buckets.print_bucket(info['bucket'])
    utils.echo_success()
    click.echo('Bucket %s added!' % info['bucket']['name'])


@main.command('bucket:list')
@utils.login_required
def list_cmd(app):
    "list all buckets you have access to"
    buckets = app.client.buckets()
    output.buckets.print_buckets(buckets)


@main.command('bucket')
@utils.bucket_option(required=True)
@utils.login_required
def bucket(app, bucket):
    "show a published bucket"
    info = app.client.bucket(bucket)
    output.buckets.print_bucket(info['bucket'])


@main.command('bucket:destroy')
@utils.bucket_option(required=True)
@utils.login_required
def bucket_destroy(app, bucket):
    "tear down a published bucket"
    app.client.delete_bucket(bucket)
    utils.echo_success()
    click.echo(' Bucket %s removed' % bucket)


@main.command('bucket:cache:add')
@utils.bucket_option(required=True)
@click.option('--url', help='The url endpoint to cache')
@click.option('--type', help='type of cache')
@click.option('--name', required=True, help='Give it a name')
@utils.login_required
def bucket_cache_add(app, bucket, url, type, name):
    "Add a cache to the bucket"

    app.client.add_url(bucket, url, name, type)

    utils.echo_success()
    click.echo(' Cache %s was added as %s' % (url, name))


@main.command('bucket:cache:remove')
@utils.bucket_option(required=True)
@click.option('-n', '--name', help='name of cache to remove')
@utils.login_required
def bucket_cache_remove(app, bucket, name):
    "Remove a cache from the bucket"

    info = app.client.remove_url(bucket, name)
    utils.echo_success()
    click.echo(' Cache %s (%s) was removed' % (info['url'], name))


@main.command(category='Build')
@utils.bucket_option(required=True)
@click.option(
    '--dryrun/--no-dryrun',
    help='only print output don\'t modify config files'
)
@application.email_option
@application.token_option
@application.password_option
@application.pass_app
def use(app, bucket, dryrun):
    "Activate and record all usage for a bucket"

    token = app.token
    if token:
        try:
            app.client.check_bucket_token(bucket, token)
        except errors.BadAuthorization:
            token = None

    if not token:
        token = setup_bucket_token(app, bucket, use_config_token=False)

    use_bucket(app, bucket, token, dryrun)


@main.command(category='Build')
@application.pass_app
def unuse(app):
    "Deactivate a bucket"
    unuse_bucket(app)


@main.command(category='Build')
@application.pass_app
def using(app):
    "Deactivate a bucket"
    using = app.config.get('using', None)
    if not using:
        click.echo('You are not currently using a bucket')
        sys.exit(1)
    else:
        click.echo('You are using bucket "%(bucket)s"' % using)

    return


@main.command('bucket:objects')
@click.option(
    '-a', '--after', required=False, default=None,
    help='Show all objects added to buckets after a date'
)
@utils.bucket_option(required=True)
@utils.login_optional
def bucket_objects(app, bucket, after=None):
    """Show the objects added to a bucket since a time"""

    if after:
        objects = app.client.objects_since(bucket, after)
    else:
        objects = app.client.objects(bucket)

    output.buckets.print_objects(objects)


@main.command('bucket:rollback')
@click.option(
    '-w', '--when', required=True, default=None,
    type=utils.datetime_type,
    help='Rollback after',
)
@utils.bucket_option(required=True)
@utils.login_optional
def bucket_rollback(app, bucket, when):
    """Show the objects added to a bucket since a time"""

    app.client.rollback(bucket, when)

    utils.echo_success()
    click.echo("Bucket %s rolled back to %s" % (bucket, when.ctime()))


@main.command('bucket:freeze')
@utils.bucket_option(required=True)
@utils.login_required
def freeze(app, bucket):
    "Freeze a bucket so it can not be modified"
    app.client.freeze(bucket)
    utils.echo_success()
    click.echo("Bucket %s frozen" % (bucket))


@main.command('bucket:unfreeze')
@utils.bucket_option(required=True)
@utils.login_required
def unfreeze(app, bucket):
    "Unfreeze a bucket so it can be modified"
    app.client.unfreeze(bucket)
    utils.echo_success()
    click.echo("Unfroze Bucket %s" % (bucket))


@main.command(category='Authentication')
@application.email_option
@application.password_option
@utils.bucket_option(required=True)
@application.pass_app
def token(app, bucket):
    "Get your authentication token"

    # Will raise not found exception
    app.client.bucket(bucket)

    token = setup_bucket_token(app, bucket)
    print("  token:", token)


@main.command()
@utils.login_optional
def info(app):
    "Fetch environment and server informations"
    output.build_info.build_info(app.client)


@main.command('setup')
def setup(app, dir):
    "Set up new bucket"


@main.command('setup:custom')
@utils.dir_option
@utils.login_required
def setup_custom(app, dir):
    "Set up new custom bucket"
    setup_bucket(app, dir, 'custom')


@main.command('setup:circle')
@utils.dir_option
@utils.login_required
def setup_circle(app, dir):
    "Set up new bucket on circleci"
    setup_bucket(app, dir, 'circleci')


# @main.command('pip')
# @utils.bucket_option(required=True)
# @utils.login_optional
# @click.argument('pip_args', nargs=-1, type=click.UNPROCESSED)
# def pip(app, bucket, pip_args):
#     print("pip_args", pip_args)
#     # execute_pip(app, bucket, pip_args)


@main.command(context_settings=dict(
    ignore_unknown_options=True,
))
@utils.bucket_option(required=True)
@click.argument('pip_args', nargs=-1, type=click.UNPROCESSED)
@utils.login_required
def pip(app, bucket, pip_args):
    """A wrapper around Python's timeit."""
    execute_pip(app, bucket, pip_args)


if __name__ == '__main__':
    main(obj={})

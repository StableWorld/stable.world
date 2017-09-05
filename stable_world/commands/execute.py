from __future__ import print_function
import click

from stable_world.interact.setup_user import setup_bucket_token
from stable_world.interact.use import check_bucket
from stable_world import executors
from stable_world import errors, utils, application

from stable_world.managers.pypi import PyPIManager
from stable_world.managers.npm import NPMManager


@click.group()
def main():
    pass


@main.command(context_settings=dict(
    ignore_unknown_options=True,
))
@utils.bucket_option(required=True)
@click.argument('curl_args', nargs=-1, type=click.UNPROCESSED)
@utils.login_required
def curl(app, bucket, curl_args):
    """A wrapper around curl"""
    executors.execute_curl(app, bucket, curl_args)


@main.command(context_settings=dict(
    ignore_unknown_options=True,
))
@utils.bucket_option(required=True)
@click.argument('pip_args', nargs=-1, type=click.UNPROCESSED)
@utils.login_required
def pip(app, bucket, pip_args):
    """A wrapper around Python's pip"""
    executors.execute_pip(app, bucket, pip_args)


@main.command(context_settings=dict(
    ignore_unknown_options=True,
))
@utils.bucket_option(required=True)
@click.argument('npm_args', nargs=-1, type=click.UNPROCESSED)
@utils.login_required
def npm(app, bucket, npm_args):
    """A wrapper around NodeJS's npm"""
    executors.execute_npm(app, bucket, npm_args)


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

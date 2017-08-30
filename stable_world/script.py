"""
This is a command
"""
from __future__ import print_function
import sys

import click

from stable_world import __version__ as sw_version
from stable_world.output import error_output
from stable_world.env import env
from stable_world.sw_logging import setup_logging
from stable_world import utils, application
from stable_world.commands import misc, bucket, ci, auth, execute

CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'],
)


@click.command(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
    cls=click.CommandCollection
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


main.add_source(auth.main)
main.add_source(bucket.main)
main.add_source(ci.main)
main.add_source(execute.main)
main.add_source(misc.main)

if __name__ == '__main__':
    main(obj={})

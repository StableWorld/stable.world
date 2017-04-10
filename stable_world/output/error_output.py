from __future__ import print_function
import sys
import os
import traceback
import time
from requests.utils import quote
from requests.exceptions import ConnectionError
import click
from stable_world.py_helpers import platform_uname
from stable_world import __version__ as version
from stable_world import config, errors

original_excepthook = sys.excepthook


def write_error_log(exctype, value, tb):

    logfile = os.path.join(config.cache_dirname, 'logs', 'debug.txt')
    try:
        if not os.path.isdir(os.path.dirname(logfile)):
            os.makedirs(os.path.dirname(logfile))
    except Exception:
        # Don't want any errors here
        click.echo("Failed to write logfile", err=True)
        original_excepthook(exctype, value, tb)

    try:
        with open(logfile, 'w') as fd:
            uname = platform_uname()
            header = '[Unhandled Exception at {}] system={}, stable.world version: {}'
            print(header.format(time.ctime(), uname.system, version), file=fd)
            traceback.print_exception(exctype, value, tb, file=fd)
        click.echo('\n    Wrote full traceback to "{}"\n'.format(logfile), err=True)
    except:
        click.echo("Failed to write logfile", err=True)
        original_excepthook(exctype, value, tb)


def brief_excepthook(exctype, value, tb):
    """
    Shorten exeptions with the base class errors.UserError
    """
    if issubclass(exctype, errors.BRIEF_ERRORS):
        click.secho("\n\n    {}: ".format(exctype.__name__), nl=False, fg='red', bold=True, err=True)
        click.echo(str(value), err=True)
        click.echo(err=True)
    elif issubclass(exctype, ConnectionError):
        click.secho("\n\n    {}: ".format(exctype.__name__), nl=False, fg='red', bold=True, err=True)
        click.echo('Could not connect to url "{}"'.format(value.request.url), err=True)
        click.echo(err=True)
    else:
        msg = "\n\n    Critical! Unhandled Exception\n    {}: ".format(exctype.__name__)
        click.secho(msg, nl=False, fg='red', bold=True, err=True)
        click.echo(str(value), err=True)
        click.echo(err=True)

        click.echo('\n    Check for updates on this exception on the issue tracker:')
        search_str = quote('is:issue {} "{}"'.format(exctype.__name__, value))
        click.echo('      ', nl=False)
        click.secho(
            'https://github.com/srossross/stable.world/issues?q={}\n'.format(search_str),
            fg='blue', underline=True, err=True
        )
        click.echo('    Or create a new issue:', err=True)
        click.echo('      ', nl=False, err=True)
        click.secho(
            'https://github.com/srossross/stable.world/issues/new',
            fg='blue', underline=True, err=True
        )

        write_error_log(exctype, value, tb)
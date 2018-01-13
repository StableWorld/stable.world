from __future__ import print_function, unicode_literals
import sys
import os
import traceback
import time
from requests.utils import quote
from requests.exceptions import ConnectionError
import click
from stable_world.py_helpers import platform_uname
from stable_world import __version__ as version
from stable_world import errors

original_excepthook = sys.excepthook

from stable_world.py_helpers import PY3

if PY3:
    unicode = str


def write_error_log(cache_dirname, exctype, value, tb):
    '''
    Write the exception to a the log file
    '''
    logfile = os.path.join(cache_dirname, 'logs', 'debug.txt')

    try:
        with open(logfile, 'w') as fd:
            uname = platform_uname()
            header = '[Unhandled Exception at {}] system={}, stable.world version: {}'
            print(header.format(time.ctime(), uname.system, version), file=fd)
            tb = '\n'.join(traceback.format_exception(exctype, value, tb))
            print(tb, file=fd)
        click.echo('\n    Wrote full traceback to "{}"\n'.format(logfile), err=True)
    except Exception:
        click.echo("Failed to write logfile", err=True)
        original_excepthook(exctype, value, tb)


def brief_excepthook(cache_dirname):
    """
    Shorten exeptions with the base class errors.UserError
    """
    def inner(exctype, value, tb):
        if issubclass(exctype, errors.BRIEF_ERRORS):
            click.secho("\n\n    {}: ".format(exctype.__name__), nl=False, fg='red', bold=True, err=True)
            click.echo(unicode(value), err=True)
            click.echo(err=True)
        elif issubclass(exctype, ConnectionError):
            click.secho("\n\n    {}: ".format(exctype.__name__), nl=False, fg='red', bold=True, err=True)
            click.echo('Could not connect to url "{}"'.format(value.request.url), err=True)
            click.echo(err=True)
        else:
            msg = "\n\n    Critical! Unhandled Exception\n    {}: ".format(exctype.__name__)
            click.secho(msg, nl=False, fg='red', bold=True, err=True)
            click.echo(unicode(value), err=True)
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

            write_error_log(cache_dirname, exctype, value, tb)
        return

    return inner

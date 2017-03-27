import sys
import platform
from requests.exceptions import ConnectionError

import click

if platform.python_version_tuple()[0] == '3':
    from configparser import Error as ConfigParserError
else:
    from ConfigParser import Error as ConfigParserError


class StableWorldError(Exception):
    def __init__(self, message, payload=None):
        Exception.__init__(self, message)
        self.payload = payload
        self.message = message


class UserError(StableWorldError):
    pass


class NotFound(UserError):
    pass


class HTTPException(UserError):

    @property
    def path(self):
        return self.payload.get('path') if self.payload else None

    @property
    def method(self):
        return self.payload.get('method', 'GET') if self.payload else 'GET'

    @property
    def quick_path(self):
        return '[%s] %s' % (self.method, self.path)

    def __str__(self):
        if self.path:
            return '%s (%s)' % (self.message, self.quick_path)
        else:
            return '%s' % self.message


class DuplicateKeyError(UserError):
    pass


class PZError(UserError):
    def log(self):
        print(self.args[0])


class PasswordError(UserError):
    def log(self):
        print('User with the email %s ' % self.args[0])


class ValidationError(UserError):
    def log(self):
        print(self.args[0])


original_excepthook = sys.excepthook

# List of exceptions that dont need a full traceback
BRIEF_ERRORS = UserError, ConfigParserError


def brief_excepthook(exctype, value, tb):
    """
    Shorten exeptions with the base class errors.UserError
    """
    if issubclass(exctype, BRIEF_ERRORS):
        click.secho("\n\n  {}: ".format(exctype.__name__), nl=False, fg='red', bold=True)
        click.echo(str(value))
        click.echo()
    elif issubclass(exctype, ConnectionError):
        click.secho("\n\n  {}: ".format(exctype.__name__), nl=False, fg='red', bold=True)
        click.echo('Could not connect to url "{}"'.format(value.request.url))
        click.echo()
    else:
        original_excepthook(exctype, value, tb)

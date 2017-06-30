from functools import wraps
from os.path import abspath
import click
from .interact.setup_user import setup_user
from . import application

from dateutil.parser import parse as parse_datetime
from datetime import datetime, timedelta
from dateutil.tz import tzlocal

dir_option = click.option(
    '--dir', default=abspath('.'),
    help='The Directory of the bucket you want to setup'
)


def echo_success():
    click.secho('  Success: ', nl=False, fg='green')


def echo_error():
    click.secho('  Error: ', nl=False, fg='red')


def echo_warning():
    click.secho('  Warning: ', nl=False, fg='magenta')


def bucket_option(required=False):
    return click.option(
        '-b', '--bucket', required=required,
        help='Name of bucket'
    )


def when_option(required=False):
    return click.option(
        '-w', '--when', required=required,
        help='Time'
    )


def localnow():
    return datetime.now().replace(tzinfo=tzlocal())


timeKeyWords = {
    'now': localnow,
    'yesterday': lambda: localnow() - timedelta(days=1),
    'last week': lambda: localnow() - timedelta(days=7),
}


def datetime_type(value):
    if value in timeKeyWords:
        return timeKeyWords[value]()

    dt = parse_datetime(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tzlocal())
    return dt


def ensure_login(app, hide_token=True):
    if app.email and app.token:
        click.echo('\n %30s: %s' % ('email', app.email))
        if hide_token:
            click.echo(' %30s: %s\n' % ('token', '*' * 10))
        else:
            click.echo(' %30s: %s\n' % ('token', app.token))
    else:
        setup_user(app)


def login_required(func):
    """
    Require login and add options to support this
    """
    @application.email_option
    @application.password_option
    @application.token_option
    @application.pass_app
    @wraps(func)
    def decorator(app, **kwargs):
        ensure_login(app)
        func(app, **kwargs)

    return decorator


def login_optional(func):
    """
    Check for login and add options to support this
    """
    @application.email_option
    @application.password_option
    @application.token_option
    @application.pass_app
    @wraps(func)
    def decorator(app, **kwargs):

        if app.email and app.password:
            setup_user(app, login_only=True)

        func(app, **kwargs)

    return decorator

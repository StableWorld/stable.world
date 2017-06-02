from functools import wraps
from os.path import abspath
import click
from .interact.setup_user import setup_user
from . import application

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
        '-p', '--bucket', required=required,
        help='Name of bucket'
    )


def tag_option(required=False):
    return click.option(
        '-t', '--tag', required=True,
        help='Name of tag in bucket'
    )


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

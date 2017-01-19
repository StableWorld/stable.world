import os
from functools import wraps
import click

from .client import Client
from .config import config
from .interact.setup_user import setup_user


email_option = click.option(
    '--email', default=os.getenv('STABLE_WORLD_EMAIL', config.get('email'))
)
password_option = click.option(
    '--password', default=os.getenv('STABLE_WORLD_PASSWORD')
)
token_option = click.option(
    '--token', default=os.getenv('STABLE_WORLD_TOKEN', config.get('token'))
)


def echo_success():
    click.secho("  Success: ", nl=False, fg='green')


def project_option(required=False):
    return click.option(
        '-p', '--project', required=required,
        help='Name of project'
    )


def tag_option(required=False):
    return click.option(
        '-t', '--tag', required=True,
        help='Name of tag in project'
    )


def ensure_login(email, password, token):

    if email and token:
        click.echo('\n %30s: %s' % ('email', email))
        click.echo(' %30s: %s\n' % ('token', '*' * 10))
        return Client(email, token)

    return setup_user(email, password, token)


def login_required(func):
    """
    Require login and add options to support this
    """
    @email_option
    @password_option
    @token_option
    @wraps(func)
    def decorator(email, password, token, **kwargs):
        client = ensure_login(email, password, token)
        func(client, **kwargs)

    return decorator


def login_optional(func):
    """
    Check for login and add options to support this
    """
    @email_option
    @password_option
    @token_option
    @wraps(func)
    def decorator(email, password, token, **kwargs):

        if email and token:
            client = Client(email, token)
        else:
            client = ensure_login(email, password, token)

        func(client, **kwargs)

    return decorator

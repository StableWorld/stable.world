from functools import wraps
from os.path import abspath
import click

from .client import Client
from .interact.setup_user import setup_user
from .env import env
from .config import config, update_token

email_option = click.option(
    '--email', default=env.STABLE_WORLD_EMAIL,
    help='Your email'
)
password_option = click.option(
    '--password', default=env.STABLE_WORLD_PASSWORD,
    help='Your password'
)
token_option = click.option(
    '--token', default=env.STABLE_WORLD_TOKEN,
    help='An authentication token'
)

dir_option = click.option(
    '--dir', default=abspath('.'),
    help='The Directory of the project you want to setup'
)


def echo_success():
    click.secho('  Success: ', nl=False, fg='green')


def echo_error():
    click.secho('  Error: ', nl=False, fg='red')


def echo_warning():
    click.secho('  Warning: ', nl=False, fg='magenta')


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


def ensure_login(email, password, token, hide_token=True):
    if email and token:
        click.echo('\n %30s: %s' % ('email', email))
        if hide_token:
            click.echo(' %30s: %s\n' % ('token', '*' * 10))
        else:
            click.echo(' %30s: %s\n' % ('token', token))
        if config.get('email') != email or config.get('token') != token:
            update_token(email=email, token=token)
    else:
        setup_user(email, password, token)

    return Client(None)


def update_config_with_args(func):
    """
    Set token and email arguments to the function
    from the config
    """
    @wraps(func)
    def decorator(**kwargs):
        if not kwargs.get('email'):
            kwargs['email'] = config.get('email')
        if not kwargs.get('token'):
            kwargs['token'] = config.get('token')
        return func(**kwargs)
    return decorator


def login_required(func):
    """
    Require login and add options to support this
    """
    @email_option
    @password_option
    @token_option
    @wraps(func)
    @update_config_with_args
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
    @update_config_with_args
    def decorator(email, password, token, **kwargs):

        client = Client(None)

        if email and password:
            setup_user(email, password, token)

        func(client, **kwargs)

    return decorator

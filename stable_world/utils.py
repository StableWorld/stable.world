from functools import wraps
from os.path import abspath
import click

from .client import Client
from .interact.setup_user import setup_user
from . import application
# from .env import env
from .config import config

# email_option = click.option(
#     '--email', default=env.STABLE_WORLD_EMAIL,
#     help='Your email'
# )
# password_option = click.option(
#     '--password', default=env.STABLE_WORLD_PASSWORD,
#     help='Your password'
# )
#
# token_option = click.option(
#     '--token', default=env.STABLE_WORLD_TOKEN,
#     help='An authentication token'
# )

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


def ensure_login(app, hide_token=True):
    if app.email and app.token:
        click.echo('\n %30s: %s' % ('email', app.email))
        if hide_token:
            click.echo(' %30s: %s\n' % ('token', '*' * 10))
        else:
            click.echo(' %30s: %s\n' % ('token', app.token))
        # if config.get('email') != email or config.get('token') != token:
        #     app.update_netrc()
    else:
        setup_user(app)

    # return Client(None)


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
    @application.email_option
    @application.password_option
    @application.token_option
    @wraps(func)
    def decorator(app, **kwargs):

        ensure_login(app)
        func(app, **kwargs)

    return decorator


def client(func):
    """
    Pass client to command
    """
    @wraps(func)
    def decorator(**kwargs):
        return func(Client(None), **kwargs)

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

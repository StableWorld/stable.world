import click
from ..config import config, update_token
from .. import errors
from ..client import Client
# from getpass import getpass

try:
    raw_input
except NameError:
    raw_input = input


def setup_user(email, password, token, login_only=False, confirm_password=True, scopes=None):
    """
    Prompt user for email and password
    """
    client = Client(None)

    click.echo(
        '\n    '
        'Welcome to stable.world! (http://stable.world)'
        '\n    '
        'Please login or create an account '
        'by entering your email and password:'
        '\n'
    )

    if not email:
        email = click.prompt(' %30s' % 'email')
    else:
        click.echo(' %30s: %s' % ('email', email))

    for i in range(3):

        if not password:
            password = click.prompt(' %30s' % 'password', hide_input=True)

        try:
            token = client.token(email, password, scopes={'api': 'write'})
            update_token(email=email, token=token)
            click.echo('\n    Welcome back %s\n\n' % email)
            return client
        except errors.NotFound:
            if login_only:
                raise
            if confirm_password:
                click.echo('\n    Hello %s, we are about to create an account for you' % email)
                click.echo('    Please confirm your password:\n')
                confirm_password = click.prompt(' %30s' % 'password', hide_input=True)
                if confirm_password != password:
                    raise errors.UserError("Passwords do no match, pelase try again")
            token = client.register(email, password)
            update_token(email=email, token=token)
            click.echo('\n    Registered new user %s\n\n' % email)
            return client
        except errors.PasswordError:
            password = None
            continue

    # TODO: follow up on this
    forgot = click.confirm('    forgot password? (yes)', default=True)
    if forgot:
        raise Exception('?')
    else:
        raise errors.UserError("Bye")


def setup_project_token(email, password, project, use_config_token=True):
    """
    Prompt user for email and password
    """
    client = Client(None)

    if config.get('token') and use_config_token:
        return config.get('token')

    email = email or config.get('email')
    password = password or config.get('password')

    click.echo(
        '\n    '
        'Welcome to stable.world! (http://stable.world)'
        '\n    '
        'To create a project token we need you to re-enter your password '
        '\n'
    )

    if not email:
        email = click.prompt(' %30s' % 'email')
    else:
        click.echo(' %30s: %s' % ('email', email))

    for i in range(3):

        if not password:
            password = click.prompt(' %30s' % 'password', hide_input=True)

        try:
            token = client.token(email, password, scopes={'project': project})
            config.update(password=password)
            return token
        except errors.PasswordError:
            password = None
            continue

    # TODO: follow up on this
    forgot = click.confirm('    forgot password? (yes)', default=True)
    if forgot:
        raise Exception('This functionality is not implemented atm')
    else:
        raise errors.UserError("Bye")

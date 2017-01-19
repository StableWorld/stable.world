import click
from ..config import update_config
from .. import errors
from ..client import Client
# from getpass import getpass

try:
    raw_input
except NameError:
    raw_input = input


def setup_user(email, password, token):

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
            client = Client.from_login_or_register(email, password)
            update_config(email=email, token=client.token)
            click.echo('\n    Logged in as %s\n\n' % email)
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

import click
from stable_world.interact.setup_user import setup_user
from stable_world import utils, application
from stable_world.interact.setup_user import setup_bucket_token


@click.group()
def main():
    pass


@main.command()
@application.email_option
@application.password_option
@application.token_option
@application.pass_app
def login(app):
    "only performs authentication step"
    setup_user(app, login_only=True)
    return


@main.command()
@application.email_option
@application.password_option
@application.token_option
@application.pass_app
def register(app):
    "only performs authentication step"
    confirm_password = not app.password
    setup_user(app, login_only=False, confirm_password=confirm_password)
    return


@main.command()
@application.pass_app
def logout(app):
    "expire local token"

    app.update_netrc(token=None, email=None)
    click.echo(
        '\n\n    '
        'Token removed from %s file.'
        '\n\n' % app.config_filename
    )
    return


@main.command()
@utils.login_optional
def whoami(app):
    "show who you are logged in as"

    email = app.client.whoami()
    click.echo('\n\n    Logged in as %s\n\n' % email)
    return


@main.command()
@application.email_option
@application.password_option
@utils.bucket_option(required=False)
@application.pass_app
def token(app, bucket):
    "Get your authentication token"

    # Will raise not found exception
    if bucket:
        app.client.bucket(bucket)

    token = setup_bucket_token(app, bucket)
    print("  token:", token)

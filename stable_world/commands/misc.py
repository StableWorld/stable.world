
import click
from stable_world import utils, output, group, application


@click.group(cls=group.StableWorldGroup)
def main():
    pass


@main.command()
@utils.login_optional
def info(app):
    "Fetch environment and server informations"
    output.build_info.build_info(app.client)


@main.command()
@click.argument('key')
@click.argument('value')
@application.pass_app
def set(app, key, value):
    """Set a config value

    e.g:

    """
    app.write_config(key, value)
    utils.echo_success()
    click.echo('key "{}" was set'.format(key))
    return

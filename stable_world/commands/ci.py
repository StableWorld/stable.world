"""
This is a command
"""
from __future__ import print_function
import click

from stable_world.interact.setup_bucket import setup_bucket
from stable_world import utils, application


@click.group()
def main():
    pass


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


@main.command('ci')
def ci(app, dir):
    "Set up stable.world in your continuous delivery pipline"


@main.command('ci:bash')
@utils.dir_option
@utils.login_required
def ci_bash(app, dir):
    "Set up stable.world in your continuous delivery pipline using bash"
    setup_bucket(app, dir, 'custom')


@main.command('ci:circle')
@utils.dir_option
@utils.login_required
def ci_circle(app, dir):
    "Set up stable.world in your continuous delivery pipline using circleci"
    setup_bucket(app, dir, 'circleci')


if __name__ == '__main__':
    main(obj={})

import click

from stable_world.context import Context

pass_app = click.make_pass_decorator(Context, ensure=True)
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class SableWorldCLI(click.Group):

    ALIAS_MAP = {}

    def list_commands(self, ctx):
        return click.Group.list_commands(self, ctx)

    def get_command(self, ctx, name):
        return click.Group.get_command(self, ctx)


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS, cls=SableWorldCLI)
@pass_app
def main(app):
    print('main', app)


@main.command()
@pass_app
def command1(app):
    'help for command1'
    print("command1", app)


if __name__ == '__main__':
    main()

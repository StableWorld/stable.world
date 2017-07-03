import click

__all__ = ('StableWorldGroup', )


class StableWorldCommand(click.Command):
    def __init__(self, category='', **kwargs):
        self.category = category
        click.Command.__init__(self, **kwargs)

    def format_subcommands(self, ctx, formatter):
        root = ctx.find_root()
        sub_commands = {
            key: value.short_help or '' for key, value in root.command.commands.items()
            if key.startswith('{}:'.format(ctx.command.name))
        }
        if sub_commands:
            with formatter.section('Commands for {}'.format(ctx.command.name)):
                formatter.write_dl(sorted(sub_commands.items()))

    def format_help(self, ctx, formatter):
        """Writes the help into the formatter if it exists.

        """

        self.format_usage(ctx, formatter)
        self.format_help_text(ctx, formatter)
        self.format_options(ctx, formatter)
        self.format_subcommands(ctx, formatter)
        self.format_epilog(ctx, formatter)


class StableWorldGroup(click.Group):

    ALIAS_MAP = {}

    def list_commands(self, ctx, all=False):
        commands = click.Group.list_commands(self, ctx)
        if all:
            return commands
        return sorted({cmd.split(':')[0] for cmd in commands})

    def get_command(self, ctx, name):
        return click.Group.get_command(self, ctx, name)

    def command(self, *args, **kwargs):
        kwargs.setdefault('cls', StableWorldCommand)
        return click.Group.command(self, *args, **kwargs)

    def format_commands(self, ctx, formatter):
        """Extra format methods for multi methods that adds all the commands
        after the options.
        """
        categories = {}

        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command.  Ignore it
            if cmd is None:
                continue

            rows = categories.setdefault(getattr(cmd, 'category', ''), [])
            help = cmd.short_help or ''
            rows.append((subcommand, help))
        for category, rows in sorted(categories.items()):
            title = '{} Commands'.format(category) if category else 'Commands'
            with formatter.section(title):
                formatter.write_dl(sorted(rows))

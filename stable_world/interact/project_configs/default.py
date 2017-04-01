from random import choice
import click
from stable_world import errors
from . import words
from .base import ProjectConfigurator


def random_project_name():
    return '%s-%s' % (choice(words.adjectives), choice(words.nouns))


class CustomProjectHelper(ProjectConfigurator):

    def setup_project_name(self):
        project_name = random_project_name()

        # TODO: fix interaction here, should not prompt user after they have entered
        while 1:
            if project_name:
                ok = click.confirm(
                    ' %30s: \'%s\' ?' % ('name your project', project_name),
                    default=True
                )
                click.echo('')
                if ok:
                    try:
                        return self.client.add_project(project_name)
                    except errors.DuplicateKeyError:
                        click.echo('')
                        tml = '  ERROR: The project "%s" alreadys exists'
                        click.echo(tml % project_name)
                        click.echo('  Project names must be unique')

            project_name = click.prompt(' %30s' % 'name your project')

    def setup_project_env(self):
        pass

    def setup_project_ci(self):
        pass

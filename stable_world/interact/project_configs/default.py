from random import choice
from stable_world.output.helpers import indent
import click
from stable_world import errors, config
from . import words
from .base import ProjectConfigurator


def random_project_name():
    'Generate a random project name'
    return '%s-%s' % (choice(words.adjectives), choice(words.nouns))


class CustomProjectHelper(ProjectConfigurator):

    @classmethod
    def is_valid(cls, project_dir):
        return True

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
                        self.project_name = project_name
                        return self.client.add_project(project_name)
                    except errors.DuplicateKeyError:
                        click.echo('')
                        tml = '  ERROR: The project "%s" alreadys exists'
                        click.echo(tml % project_name)
                        click.echo('  Project names must be unique')

            project_name = click.prompt(' %30s' % 'name your project')

    def setup_project_env(self):

        click.echo('')
        click.echo(
            '  You need to navigate to where your project build lives and give your CI '
            'this secure environment variable:\n'
        )
        click.echo('    Name:')
        click.secho('    STABLE_WORLD_TOKEN', dim=True)
        click.echo('    Value:')
        click.secho('    {}'.format(config.config['token']), dim=True)

        click.pause('\n  Got it? (Press any key to continue ...)')

    def setup_project_ci(self):

        add_lines = [
            'curl {url}/install | sudo bash -s -- rc'.format(url=config.config['url']),
            'stable.world use -p {project_name} -t ' +
            'build${{CIRCLE_BUILD_NUM}}'.format(project_name=self.project_name)
        ]
        default = indent('\n'.join(add_lines), '    + ')
        click.echo('')
        click.echo('  You need to add the following lines to your build script:')
        click.echo('')
        click.secho(default, fg='green')
        click.echo('')
        click.echo('  You need commit this and push to your repo')

        click.pause('\n  Got it? (Press any key to continue ...)')

    def setup(self):
        pass

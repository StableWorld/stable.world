from random import choice
import click
from . import words
from .. import errors


def setup_space(client):

    project_name = '%s-%s' % (choice(words.adjectives), choice(words.nouns))

    # TODO: fix interaction here, should not prompt user after they have entered
    while 1:
        if project_name:
            ok = click.confirm(
                ' %20s: \'%s\' ?' % ('name your project', project_name),
                default=True
            )
            if ok:
                try:
                    client.add_project(project_name)
                    break
                except errors.DuplicateKeyError:
                    click.echo('')
                    tml = '    ERROR: The project "%s" alreadys exists'
                    click.echo(tml % project_name)
                    click.echo('    Project names must be unique')

        project_name = click.prompt(' %20s' % 'name your project')

    click.echo('    Project %s added!' % project_name)
    return project_name

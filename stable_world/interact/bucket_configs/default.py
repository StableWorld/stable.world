from random import choice
from stable_world.output.helpers import indent
import click
from stable_world import errors
from . import words
from .base import BucketConfigurator


def random_bucket_name():
    'Generate a random bucket name'
    return '%s-%s' % (choice(words.adjectives), choice(words.nouns))


class CustomBucketHelper(BucketConfigurator):

    @classmethod
    def is_valid(cls, working_dir):
        return True

    def setup(self):
        # TODO: test me
        click.echo('  Setup a new bucket:\n')

    def setup_bucket_name(self):
        bucket_name = random_bucket_name()

        # TODO: fix interaction here, should not prompt user after they have entered
        while 1:
            if bucket_name:
                ok = click.confirm(
                    ' %30s: \'%s\' ?' % ('name your bucket', bucket_name),
                    default=True
                )
                click.echo('')
                if ok:
                    try:
                        self.bucket_name = bucket_name
                        return self.client.add_bucket(bucket_name)
                    except errors.DuplicateKeyError:
                        click.echo('')
                        tml = '  ERROR: The bucket "%s" alreadys exists'
                        click.echo(tml % bucket_name)
                        click.echo('  Bucket names must be unique')

            bucket_name = click.prompt(' %30s' % 'name your bucket')

    def setup_bucket_env(self):

        token = self.get_token()

        click.echo('')
        click.echo(
            '  You need to navigate to where your bucket build lives and give your CI '
            'this secure environment variable:\n'
        )
        click.echo('    Name:')
        click.secho('    STABLE_WORLD_TOKEN', dim=True)
        click.echo('    Value:')
        click.secho('    {}'.format(token), dim=True)

        click.pause('\n  Got it? (Press any key to continue ...)')

    def setup_bucket_ci(self):

        add_lines = [
            'curl {url}/install | sudo bash -s -- rc'.format(url=self.site_url),
            'stable.world use -b {bucket_name} -t ' +
            'build${{CIRCLE_BUILD_NUM}}'.format(bucket_name=self.bucket_name)
        ]
        default = indent('\n'.join(add_lines), '    + ')
        click.echo('')
        click.echo('  You need to add the following lines to your build script:')
        click.echo('')
        click.secho(default, fg='green')
        click.echo('')
        click.echo('  You need commit this and push to your repo')

        click.pause('\n  Got it? (Press any key to continue ...)')

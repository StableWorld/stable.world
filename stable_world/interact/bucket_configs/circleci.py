from os.path import isfile, join, exists
import re
import click
import logging

from stable_world.output.helpers import indent
from stable_world.py_helpers import ConfigParser
from stable_world import errors
from stable_world.interact.yaml_insert import yaml_add_lines_to_machine_pre

from .base import BucketConfigurator

logger = logging.getLogger(__name__)

GIT_URL_RE = re.compile(
    '^(git@(?P<sshhost>[\w.]+):)'
    '|(https://(.*?@)?(?P<httphost>[\w.]+)/)'
    '(?P<bucket>[\w.]+/[\w.]+?)'
    '(.git)?$'
)


class CircleBucketHelper(BucketConfigurator):

    @classmethod
    def is_valid(cls, working_dir):
        logger.info('Found CircleCI bucket "{}"'.format(working_dir))
        if isfile(join(working_dir, 'circle.yml')):
            return True

        logger.info('Could not find circle.yml file in {}'.format(working_dir))

    def get_git_remote(self):
        parser = ConfigParser()
        parser.read(join(self.working_dir, '.git', 'config'))
        return parser.get('remote "origin"', 'url')

    def __init__(self, *args):
        BucketConfigurator.__init__(self, *args)

    def setup(self):
        # TODO: configur git remote
        click.echo('  Setup your CircleCI Bucket:\n')

        uri = self.get_git_remote()

        match = GIT_URL_RE.match(uri)

        if not match:
            raise errors.UserError('Literally can not even match %s' % uri)

        self.values = GIT_URL_RE.match(uri).groupdict()
        self.initial_bucket_name = self.values.get('bucket').replace('/', '-')

    def setup_bucket_env(self):
        host = self.values.get('httphost') or self.values.get('sshhost')

        repo_part = None
        if host == 'github.com':
            repo_part = 'gh'
        elif host == 'bitbucket.org':
            repo_part = 'bb'

        bucket = self.values.get('bucket')

        circle_url = 'https://circleci.com/{repo_part}/{bucket}/edit#env-vars'.format(
            repo_part=repo_part, bucket=bucket
        )

        click.echo('')
        token = self.get_token()
        click.echo(
            '  You need to navigate to your circleci bucket '
            'and set a secure environment variable:'
        )
        click.echo('\n    Go to ', nl=False)
        click.secho('{}'.format(circle_url), fg='blue', underline=True, nl=False)
        click.echo(' and click "Add Variable"\n')
        click.echo('    Name:')
        click.secho('    STABLE_WORLD_TOKEN', dim=True)
        click.echo('    Value:')
        click.secho('    {}'.format(token), dim=True)
        ok = click.confirm('\n  Launch browser', default=True)
        if ok:
            click.launch(circle_url)

    def setup_bucket_ci(self):
        circle_yaml = join(self.working_dir, 'circle.yml')

        if exists(circle_yaml):
            with open(circle_yaml) as fd:
                text = fd.read()
        else:
            text = ''

        add_lines = [
            'curl {url}/install | sudo bash -s -- rc'.format(url=self.site_url),
            'stable.world use -b {bucket_name} -t ' +
            'build${{CIRCLE_BUILD_NUM}}'.format(bucket_name=self.bucket_name)
        ]

        default = indent(yaml_add_lines_to_machine_pre('', add_lines), '    + ')
        if 'stable.world use' in text:
            click.echo('  It looks like you are already using stable.world')
            click.echo('  Your confiuration should looke like this:')
            click.echo('')
            click.secho(default, fg='green')
        else:

            new_text = yaml_add_lines_to_machine_pre(text, add_lines)
            with open(circle_yaml, 'w') as fd:
                fd.write(new_text)

            click.echo('  The following lines were added to your circle.yml')
            click.echo('')
            click.secho(default, fg='green')
            click.echo('')
            click.echo('  You need commit this and push to your repo')

        click.pause('  Got it? (Press any key to continue ...)')

    def setup_bucket_name(self):

        bucket_name = self.initial_bucket_name

        while 1:
            if bucket_name:
                ok = click.confirm(
                    ' %30s: \'%s\'?' % ('name your bucket', bucket_name),
                    default=True
                )
                click.echo('')
                if ok:
                    try:
                        self.client.add_bucket(bucket_name)
                        break
                    except errors.DuplicateKeyError:
                        click.echo('')
                        tml = '  The bucket "%s" alreadys exists'
                        click.secho('  Warning: ', nl=False, fg='magenta')
                        click.echo(tml % bucket_name)
                        click.echo('  Bucket names must be unique')
                        ok = click.confirm('Use existing bucket?', default=False)
                        if ok:
                            break
                        else:
                            continue

            bucket_name = click.prompt(' %30s' % 'name your bucket')

        self.bucket_name = bucket_name

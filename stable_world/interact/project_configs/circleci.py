from os.path import isfile, join
import re
import click

from stable_world.output.helpers import indent
from stable_world.py_helpers import ConfigParser
from stable_world import errors, config
from stable_world.interact.yaml_insert import yaml_add_lines_to_machine_pre

from .base import ProjectConfigurator

GIT_URL_RE = re.compile(
    '^(git@(?P<sshhost>[\w.]+):)'
    '|(https://(.*?@)?(?P<httphost>[\w.]+)/)'
    '(?P<project>[\w.]+/[\w.]+?)'
    '(.git)?$'
)


class CircleProjectHelper(ProjectConfigurator):

    @classmethod
    def is_valid(cls, project_dir):
        if isfile(join(project_dir, 'circle.yml')):
            return True
        if isfile(join(project_dir, 'circle.yaml')):
            return True

    def get_git_remote(self):
        parser = ConfigParser()
        parser.read(join(self.project_dir, '.git', 'config'))
        return parser.get('remote "origin"', 'url')

    def __init__(self, *args):
        ProjectConfigurator.__init__(self, *args)

    def setup(self):
        # TODO: configur git remote
        uri = self.get_git_remote()

        match = GIT_URL_RE.match(uri)

        if not match:
            raise errors.UserError('Literally can not even match %s' % uri)

        self.values = GIT_URL_RE.match(uri).groupdict()
        self.initial_project_name = self.values.get('project').replace('/', '-')

    def setup_project_env(self):
        host = self.values.get('httphost') or self.values.get('sshhost')

        repo_part = None
        if host == 'github.com':
            repo_part = 'gh'
        elif host == 'bitbucket.org':
            repo_part = 'bb'

        project = self.values.get('project')

        circle_url = 'https://circleci.com/{repo_part}/{project}/edit#env-vars'.format(
            repo_part=repo_part, project=project
        )

        click.echo('')
        click.echo(
            '  You need to navigate to your circleci project '
            'and set a secure environment variable:'
        )
        click.echo('\n    Go to ', nl=False)
        click.secho('{}'.format(circle_url), fg='blue', underline=True, nl=False)
        click.echo(' and click "Add Variable"\n')
        click.echo('    Name:')
        click.secho('    STABLE_WORLD_TOKEN', dim=True)
        click.echo('    Value:')
        click.secho('    {}'.format(config.config['token']), dim=True)
        ok = click.confirm('\n  Launch browser', default=True)
        if ok:
            click.launch(circle_url)

    def setup_project_ci(self):
        circle_yaml = join(self.project_dir, 'circle.yml')

        with open(circle_yaml) as fd:
            text = fd.read()

        add_lines = [
            'curl {url}/install | sudo bash -s -- rc'.format(url=config.config['url']),
            'stable.world use -p {project_name} -t ' +
            'build${{CIRCLE_BUILD_NUM}}'.format(project_name=self.project_name)
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

    def setup_project_name(self):

        project_name = self.initial_project_name

        while 1:
            if project_name:
                ok = click.confirm(
                    ' %30s: \'%s\'?' % ('name your project', project_name),
                    default=True
                )
                click.echo('')
                if ok:
                    try:
                        self.client.add_project(project_name)
                        break
                    except errors.DuplicateKeyError:
                        click.echo('')
                        tml = '  The project "%s" alreadys exists'
                        click.secho('  Warning: ', nl=False, fg='magenta')
                        click.echo(tml % project_name)
                        click.echo('  Project names must be unique')
                        ok = click.confirm('Use existing project?', default=False)
                        if ok:
                            break
                        else:
                            continue

            project_name = click.prompt(' %30s' % 'name your project')

        self.project_name = project_name

from random import choice
import click
from . import words
from stable_world.interact.setup_user import setup_project_token


def random_project_name():
    return '%s-%s' % (choice(words.adjectives), choice(words.nouns))


class ProjectConfigurator(object):
    """
    """
    CONFIGS_HELPERS = {}
    CONFIGS_HELPER_DEFAULT = None

    @staticmethod
    def register(key, detector):
        ProjectConfigurator.CONFIGS_HELPERS[key] = detector

    @staticmethod
    def get(key, app, project_dir):
        Cls = ProjectConfigurator.CONFIGS_HELPERS[key]
        return Cls(app, project_dir)

    @staticmethod
    def default(key):
        ProjectConfigurator.CONFIGS_HELPER_DEFAULT = 'custom'

    @classmethod
    def detect(cls, app, project_dir):
        for detector in ProjectConfigurator.CONFIGS_HELPERS.values():
            if detector.is_valid(project_dir):
                return detector(app, project_dir)

        if cls.CONFIGS_HELPER_DEFAULT:
            return cls.CONFIGS_HELPER_DEFAULT(app, project_dir)

    def __init__(self, app, project_dir):
        self.app = app
        self.client = app.client
        self.project_dir = project_dir

    @property
    def site_url(self):
        return self.app.config['url']

    def setup_project_name(self):
        raise NotImplementedError()

    def setup_project_env(self):
        raise NotImplementedError()

    def setup_project_ci(self):
        raise NotImplementedError()

    def success(self):
        click.secho('  Success, your build is now secure!', fg='green')
        click.echo('')

    def get_token(self):
        return setup_project_token(self.app, project=self.project_name, use_config_token=False)

from random import choice
import click
from . import words


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
    def get(key, client, project_dir):
        Cls = ProjectConfigurator.CONFIGS_HELPERS[key]
        return Cls(client, project_dir)

    @staticmethod
    def default(key):
        ProjectConfigurator.CONFIGS_HELPER_DEFAULT = 'custom'

    @classmethod
    def detect(cls, client, project_dir):
        for detector in ProjectConfigurator.CONFIGS_HELPERS.values():
            if detector.is_valid(project_dir):
                return detector(client, project_dir)

        if cls.CONFIGS_HELPER_DEFAULT:
            return cls.CONFIGS_HELPER_DEFAULT(client, project_dir)

    def __init__(self, client, project_dir):
        self.client = client
        self.client = client
        self.project_dir = project_dir

    def setup_project_name(self):
        raise NotImplementedError()

    def setup_project_env(self):
        raise NotImplementedError()

    def setup_project_ci(self):
        raise NotImplementedError()

    def success(self):
        click.secho('  Success, your build is now secure!', fg='green')
        click.echo('')

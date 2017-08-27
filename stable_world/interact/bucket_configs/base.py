from random import choice
import click
from . import words
from stable_world.interact.setup_user import setup_bucket_token


def random_bucket_name():
    return '%s-%s' % (choice(words.adjectives), choice(words.nouns))


class BucketConfigurator(object):
    """
    """
    CONFIGS_HELPERS = {}
    CONFIGS_HELPER_DEFAULT = None

    @staticmethod
    def register(key, detector):
        BucketConfigurator.CONFIGS_HELPERS[key] = detector

    @staticmethod
    def get(key, app, working_dir):
        Cls = BucketConfigurator.CONFIGS_HELPERS[key]
        return Cls(app, working_dir)

    @staticmethod
    def default(key):
        BucketConfigurator.CONFIGS_HELPER_DEFAULT = 'custom'

    @classmethod
    def detect(cls, app, working_dir):
        for detector in BucketConfigurator.CONFIGS_HELPERS.values():
            if detector.is_valid(working_dir):
                return detector(app, working_dir)

        if cls.CONFIGS_HELPER_DEFAULT:
            return cls.CONFIGS_HELPER_DEFAULT(app, working_dir)

    def __init__(self, app, working_dir):
        self.app = app
        self.client = app.client
        self.working_dir = working_dir

    @property
    def site_url(self):
        return self.app.config['STABLE_WORLD_URL']

    def setup_bucket_name(self):
        raise NotImplementedError()

    def setup_bucket_env(self):
        raise NotImplementedError()

    def setup_bucket_ci(self):
        raise NotImplementedError()

    def success(self):
        click.secho('  Success, your build is now secure!', fg='green')
        click.echo('')

    def get_token(self):
        return setup_bucket_token(self.app, bucket=self.bucket_name, use_config_token=False)

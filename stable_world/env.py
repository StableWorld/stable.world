"""
All environment lookups in one place so we can see what is being used
"""

import os
__all__ = ('env',)


class EnvProperty(object):
    def __init__(self, key, default, doc):
        self.key = key
        self.default = default
        self.doc = doc

    @property
    def exists(self):
        return self.key in os.environ

    @property
    def value(self):
        return os.getenv(self.key, self.default)

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return os.getenv(self.key, self.default)


class Environment(object):

    STABLE_WORLD_CONFIG = EnvProperty(
        'STABLE_WORLD_CONFIG',
        os.path.join('~', '.config', 'stable.world.ini'),
        'Path to config file'
    )
    STABLE_WORLD_CACHE_DIR = EnvProperty(
        'STABLE_WORLD_CACHE_DIR',
        os.path.join('~', '.cache', 'stable.world'),
        'Path to cache directory'
    )

    STABLE_WORLD_URL = EnvProperty(
        'STABLE_WORLD_URL',
        'https://stable.world',
        'url of the stabl.world site to use'
    )

    STABLE_WORLD_EMAIL = EnvProperty(
        'STABLE_WORLD_EMAIL', None,
        'email of current user'
    )

    STABLE_WORLD_VERIFY_HTTPS = EnvProperty(
        'STABLE_WORLD_VERIFY_HTTPS', None,
        'path to a CA_BUNDLE file or directory with '
        'certificates of trusted CAs (use "off" to disable https verification [DANGEROUS])'
    )

    STABLE_WORLD_PASSWORD = EnvProperty(
        'STABLE_WORLD_PASSWORD', None,
        'password'
    )

    STABLE_WORLD_TOKEN = EnvProperty(
        'STABLE_WORLD_TOKEN', None,
        'Authentication token'
    )

    DEBUG = EnvProperty(
        'DEBUG',
        '',
        'Enable debug output'
    )

    @classmethod
    def env_props(cls):
        return [prop for prop in vars(cls).values() if isinstance(prop, EnvProperty)]

    @property
    def overrides(self):
        result = {}
        for env_prop in self.env_props():
            if env_prop.exists:
                result[env_prop.key] = env_prop.value

        return result


env = Environment()

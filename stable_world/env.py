"""
All environment lookups in one place so we can see what is being used
"""

import os
__all__ = ['env']

class EnvProperty(object):
    def __init__(self, key, default, doc):
        self.key = key
        self.default = default
        self.doc = doc

    def __get__(self, instance, owner):
        return os.getenv(self.key, self.default)


class Environment(object):

    STABLE_WORLD_CONFIG = EnvProperty(
        'STABLE_WORLD_CONFIG',
        os.path.join('~', '.stable.world'),
        'Path to config file'
    )

    STABLE_WORLD_URL = EnvProperty(
        'STABLE_WORLD_URL',
        'https://probably.stable.world',
        'url of the stabl.world site to use'
    )

    STABLE_WORLD_EMAIL = EnvProperty(
        'STABLE_WORLD_EMAIL', None,
        'email of current user'
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


env = Environment()

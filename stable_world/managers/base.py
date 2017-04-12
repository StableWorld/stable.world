from __future__ import unicode_literals

import os
import click
from .push_file import push_file, pull_file
from ..config import config
from stable_world.py_helpers import urlparse, urlunparse


class BaseManager(object):

    NAME = None
    PROGRAM = None

    @classmethod
    def enabled(cls):
        if cls.PROGRAM is None:
            return True

        for path in os.getenv('PATH', '').split(os.pathsep):
            if os.path.isfile(os.path.join(path, cls.PROGRAM)):
                return True

    def __init__(self, project, create_tag, cache_list, pinned_to, dryrun):

        self.project = project
        self.create_tag = create_tag
        self.cache_list = cache_list
        self.pinned_to = pinned_to
        if pinned_to:
            self.tag = pinned_to['name']
        else:
            self.tag = self.create_tag

        self.dryrun = dryrun

        cache_info = list(cache_list)
        if not cache_info:
            return {}

        assert len(cache_info) == 1
        self.cache_name, self.cache_info = cache_info[0]

    @property
    def config_file(self):
        raise NotImplementedError()

    @property
    def cache_dir(self):
        part = '{}-{}-{}'.format(self.project, self.tag, self.NAME)
        cache_dir = os.path.join('~', '.cache', 'stable.world', part)
        return os.path.expanduser(cache_dir)

    def get_base_url(self, basicAuthRequired=False):

        api_url = config['url']

        if basicAuthRequired:
            api_uri = urlparse(api_url)
            api_url = urlunparse(api_uri._replace(netloc='{}:{}@{}'.format(
                config['email'],
                config['token'],
                api_uri.netloc
            )))

        if self.pinned_to:
            return '%s/cache/%s/%s/%s/%s/' % (api_url, 'replay', self.project, self.tag, self.cache_name)
        else:
            return '%s/cache/%s/%s/%s/%s/' % (api_url, 'record', self.project, self.tag, self.cache_name)

    def use(self):
        if not self.dryrun:
            push_file(self.config_file)

        return self.update_config_file()

    @classmethod
    def unuse(cls, info):
        if not info:
            return

        for config_file in info.get('config_files', []):
            click.echo('Removing {} config file "{}"'.format(cls.NAME, config_file))
            pull_file(config_file)

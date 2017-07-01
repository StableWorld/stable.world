from __future__ import unicode_literals

import os
import click
from pipes import quote
from .push_file import push_file, pull_file
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

    def __init__(self, site_url, urls, bucket, token, dryrun):

        self.site_url = site_url
        self.bucket = bucket
        self.token = token

        self.dryrun = dryrun

        self.cache_name = self.NAME
        self.cache_info = urls[self.NAME]

    @property
    def config_file(self):
        raise NotImplementedError()

    @property
    def cache_dir(self):
        cache_dir = os.path.join('~', '.cache', 'stable.world', self.bucket)
        return os.path.expanduser(cache_dir)

    def get_base_url(self, basicAuthRequired=False):

        site_url = self.site_url
        if basicAuthRequired:
            site_uri = urlparse(self.site_url)
            site_url = urlunparse(site_uri._replace(netloc='{}:{}@{}'.format(
                'token',
                self.token,
                site_uri.netloc
            )))

        return '%s/cache/%s/' % (site_url, self.cache_name)

    def use(self):
        if not self.dryrun:
            push_file(self.config_file)

        return self.update_config_file()

    @classmethod
    def unuse(cls, info):
        if not info:
            return

        for config_file in info.get('config_files', []):
            click.echo('Removing {} config file {}'.format(cls.NAME, quote(config_file)))
            pull_file(config_file)

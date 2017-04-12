from __future__ import print_function
import os
import sys
import click

from ..config import config
from .push_file import push_file
from .base import BaseManager


def write_channels(channels, fd):
    print('channels:', file=fd)
    for channel in channels:
        print(' -', channel, file=fd)


def make_channel_url(project, create_tag, pinned_to):
    def _make_channel_url(cache_name, cache_info):
        cache_url = cache_info['url']

        if pinned_to:
            sw_url = '%s/cache/replay/%s/%s/%s/' % (config['url'], project, pinned_to['name'], cache_name)
        else:
            sw_url = '%s/cache/record/%s/%s/%s/' % (config['url'], project, create_tag, cache_name)

        channel = cache_info['config']['channel']
        return channel.replace(cache_url, sw_url)

    return _make_channel_url


class CondaManager(BaseManager):
    NAME = 'conda'
    PROGRAM = 'conda'

    @property
    def config_file():
        return os.path.join(os.path.expanduser('~'), '.condarc')

    def use(self):

        cache_infos = list(cache_list)
        if not cache_infos:
            return {}

        create_channel = make_channel_url(project, create_tag, pinned_to)
        channels = [create_channel(cache_name, cache_info) for cache_name, cache_info in cache_infos]


        if dryrun:
            click.echo('  %-30s %s' % ('Dryrun: Would have written config file', conda_config_file))
            click.echo('---')
            write_channels(channels, sys.stdout)
            click.echo('---')
        else:
            push_file(conda_config_file)
            click.echo('  %-30s %s' % ('Writing conda config file', conda_config_file))
            with open(conda_config_file, 'w') as fd:
                write_channels(channels, fd)

        return {'config_files': [conda_config_file]}

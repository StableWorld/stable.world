import os
import sys
import click
from yaml import safe_dump

from ..config import config
from .push_file import push_file, pull_file

CONDA_PREFIX = None

for path in os.getenv('PATH', '').split(os.pathsep):
    if os.path.isfile(os.path.join(path, 'conda')):
        CONDA_PREFIX = path


def get_config_file():
    return os.path.join(os.path.expanduser('~'), '.condarc')


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


def use(project, create_tag, cache_list, pinned_to, dryrun):

    cache_infos = list(cache_list)
    if not cache_infos:
        return {}

    create_channel = make_channel_url(project, create_tag, pinned_to)
    channels = [create_channel(cache_name, cache_info) for cache_name, cache_info in cache_infos]

    conda_config_file = get_config_file()

    if dryrun:
        click.echo('  %-30s %s' % ('Dryrun: Would have written config file', conda_config_file))
        click.echo('---')
        safe_dump({'channels': channels}, sys.stdout, default_flow_style=False)
        click.echo('---')
    else:
        push_file(conda_config_file)
        click.echo('  %-30s %s' % ('Writing conda config file', conda_config_file))
        with open(conda_config_file, 'w') as fd:
            safe_dump({'channels': channels}, fd, default_flow_style=False)

    return {'config_files': [conda_config_file]}


def unuse(info):
    if not info:
        return
    for config_file in info.get('config_files', []):
        click.echo('  %-30s %s' % ('Removing conda config file', config_file))
        pull_file(config_file)

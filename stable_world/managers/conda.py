import os
from urllib.parse import urlparse

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
    token = config['token']
    api = urlparse(config['url'])
    if pinned_to:
        authenticated_url = '%s://%s' % (api.scheme, api.netloc)
    else:
        authenticated_url = '%s://token:%s@%s' % (api.scheme, token, api.netloc)

    def _make_channel_url(cache_name):
        if pinned_to:
            return '%s/replay/%s/%s' % (authenticated_url, project, cache_name)
        else:
            return '%s/record/%s/%s/%s' % (authenticated_url, project, create_tag, cache_name)
    return _make_channel_url


def use(project, create_tag, cache_list, pinned_to):

    cache_info = list(cache_list)
    if not cache_info:
        return {}

    create_channel = make_channel_url(project, create_tag, pinned_to)
    channels = [create_channel(cache_name) for cache_name, _ in cache_info]

    conda_config_file = get_config_file()
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

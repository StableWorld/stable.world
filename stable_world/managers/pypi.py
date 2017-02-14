import os
import sys
import platform

from configparser import ConfigParser
import click

from .push_file import push_file, pull_file
from ..config import config
from stable_world import errors
PIP_PREFIX = None

for path in os.getenv('PATH', '').split(os.pathsep):
    if os.path.isfile(os.path.join(path, 'pip')):
        PIP_PREFIX = path


def get_config_file():
    uname = platform.uname()
    if uname.system == 'Linux':
        return os.path.expanduser('~/.config/pip/pip.conf')
    elif uname.system == 'Darwin':
        return os.path.expanduser('~/Library/Application Support/pip/pip.conf')
    elif uname.system == 'Windows':
        return '%s\pip\pip.ini' % os.getenv('APPDATA')
    else:
        raise errors.UserError('Unsupported platform %s' % uname.system)


def get_cache_dir(project, tag):
    return os.path.join(PIP_PREFIX, 'cache', '%s-%s-pypi' % (project, tag))


def use(project, create_tag, cache_list, pinned_to, dryrun):

    if not PIP_PREFIX:
        click.echo('Pip not installed, not configuring PIP')
        return {}

    cache_info = list(cache_list)
    if not cache_info:
        return {}

    assert len(cache_info) == 1
    cache_name, cache_info = cache_info[0]

    api_url = config['url']

    if pinned_to:
        sw_url = '%s/cache/replay/%s/%s/' % (api_url, project, cache_name)
        cache_dir = get_cache_dir(project, pinned_to['name'])
    else:
        sw_url = '%s/cache/record/%s/%s/%s/' % (api_url, project, create_tag, cache_name)
        cache_dir = get_cache_dir(project, create_tag)

    pip_config_file = get_config_file()
    parser = ConfigParser()

    if os.path.isfile(pip_config_file):
        with open(pip_config_file) as fd:
            parser.read(fd)

    if 'global' not in parser.sections():
        parser.add_section('global')

    cache_url = cache_info['url']
    pypi_index = cache_info['config']['global']['index-url']
    pypi_index = pypi_index.replace(cache_url, sw_url)
    parser.set('global', 'index-url', pypi_index)
    parser.set('global', 'cache-dir', cache_dir)

    if dryrun:
        click.echo('  %-30s %s' % ('Dryrun: Would have written config file', pip_config_file))
        click.echo('---')
        parser.write(sys.stdout)
        click.echo('---')
    else:
        click.echo('  %-30s %s' % ('Writing pip config file', pip_config_file))

        if not os.path.exists(os.path.dirname(pip_config_file)):
            os.makedirs(os.path.dirname(pip_config_file), exist_ok=True)

        push_file(pip_config_file)
        with open(pip_config_file, 'w') as fd:
            parser.write(fd)

    return {'config_files': [pip_config_file]}


def unuse(info):
    if not info:
        return
    for config_file in info.get('config_files', []):
        click.echo('  %-30s %s' % ('Removing pip config file', config_file))
        pull_file(config_file)

from __future__ import unicode_literals
from mock import patch
import io

from stable_world.managers.npm import NPMManager


@patch('stable_world.managers.npm.open')
def test_npm_manager(mock_open):

    cache_info = {'url': 'http://pypi/', 'config': {'registry': 'http://npm/registry'}}
    mgr = NPMManager(
        'https://mock',
        project='project',
        cache_list=[('name', cache_info)],
        token='token',
        dryrun=False
    )

    npm_config_io = mock_open().__enter__.return_value = io.StringIO()

    mgr.use()

    npm_config = npm_config_io.getvalue()

    assert 'registry=https://mock/cache/name/' in npm_config
    assert '_auth=dG9rZW46dG9rZW4=' in npm_config


@patch('stable_world.managers.npm.open')
def test_npm_manager_pinned(mock_open):

    cache_info = {'url': 'http://pypi/', 'config': {'registry': 'http://npm/registry'}}
    mgr = NPMManager(
        'https://mock',
        project='project',
        cache_list=[('cacheName', cache_info)],
        token='token',
        dryrun=False
    )

    npm_config_io = mock_open().__enter__.return_value = io.StringIO()

    mgr.use()

    npm_config = npm_config_io.getvalue()

    assert 'registry=https://mock/cache/cacheName/' in npm_config
    assert '_auth=dG9rZW46dG9rZW4=' in npm_config

from __future__ import unicode_literals
from mock import patch
import io

from stable_world.managers.npm import NPMManager


@patch('stable_world.managers.base.config')
@patch('stable_world.managers.npm.open')
def test_npm_manager(mock_open, mock_config):

    cache_info = {'url': 'http://pypi/', 'config': {'registry': 'http://npm/registry'}}
    mgr = NPMManager(
        project='project',
        create_tag='tag1',
        cache_list=[('name', cache_info)],
        pinned_to=None,
        dryrun=False
    )

    mock_config.__getitem__ = lambda sd, item: {
        'url': 'https://mock',
        'token': 'mockToken',
        'email': 'mock@email'
    }[item]

    npm_config_io = mock_open().__enter__.return_value = io.StringIO()

    mgr.use()

    npm_config = npm_config_io.getvalue()

    assert 'registry=https://mock@email:mockToken@mock/cache/name/' in npm_config


@patch('stable_world.managers.base.config')
@patch('stable_world.managers.npm.open')
def test_npm_manager_pinned(mock_open, mock_config):

    cache_info = {'url': 'http://pypi/', 'config': {'registry': 'http://npm/registry'}}
    mgr = NPMManager(
        project='project',
        create_tag='tag1',
        cache_list=[('cacheName', cache_info)],
        pinned_to={'name': 'pinnedTag'},
        dryrun=False
    )

    mock_config.__getitem__ = lambda sd, item: {
        'url': 'https://mock',
        'token': 'mockToken',
        'email': 'mock@email'
    }[item]

    npm_config_io = mock_open().__enter__.return_value = io.StringIO()

    mgr.use()

    npm_config = npm_config_io.getvalue()

    assert 'registry=https://mock@email:mockToken@mock/cache/cacheName/' in npm_config

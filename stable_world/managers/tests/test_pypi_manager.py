from __future__ import unicode_literals

from mock import patch
import io
from stable_world.managers.pypi import PyPIManager
from stable_world.py_helpers import PY2


class AnyIO(io.StringIO):
    def write(self, data):
        if PY2 and not isinstance(data, unicode):
            # F**k unicode in python2
            data = data.decode()

        return io.StringIO.write(self, data)


@patch('stable_world.managers.base.config')
@patch('stable_world.managers.pypi.open')
def test_pypi_manager(mock_open, mock_config):

    cache_info = {'url': 'http://pypi/', 'config': {'global': {'index-url': 'http://pypi/index'}}}
    mgr = PyPIManager(
        project='project',
        create_tag='tag1',
        cache_list=[('name', cache_info)],
        pinned_to=None,
        dryrun=False
    )

    mock_config.__getitem__ = lambda sd, item: {'url': 'https://mock'}[item]
    pip_config_io = mock_open().__enter__.return_value = AnyIO()

    mgr.use()

    pip_config = pip_config_io.getvalue()

    assert 'index-url = https://mock/cache/record/project/tag1/name/index' in pip_config
    assert '.cache/stable.world/project-tag1-pypi' in pip_config


@patch('stable_world.managers.base.config')
@patch('stable_world.managers.pypi.open')
def test_pypi_manager_pinned(mock_open, mock_config):

    cache_info = {'url': 'http://pypi/', 'config': {'global': {'index-url': 'http://pypi/index'}}}
    mgr = PyPIManager(
        project='project',
        create_tag='tag1',
        cache_list=[('name', cache_info)],
        pinned_to={'name': 'pin1'},
        dryrun=False
    )

    mock_config.__getitem__ = lambda sd, item: {'url': 'https://mock'}[item]
    pip_config_io = mock_open().__enter__.return_value = AnyIO()

    mgr.use()

    pip_config = pip_config_io.getvalue()

    assert 'index-url = https://mock/cache/replay/project/pin1/name/index' in pip_config
    assert '.cache/stable.world/project-pin1-pypi' in pip_config
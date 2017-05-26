from __future__ import unicode_literals

from mock import patch
import io
from stable_world.managers.pypi import PyPIManager
from stable_world.py_helpers import PY2


class AnyIO(io.StringIO):
    def write(self, data):
        if PY2 and not isinstance(data, unicode):  # noqa: F821
            # F**k unicode in python2
            data = data.decode()

        return io.StringIO.write(self, data)


@patch('stable_world.managers.pypi.open')
def test_pypi_manager(mock_open):

    cache_info = {'url': 'http://pypi/', 'config': {'global': {'index-url': 'http://pypi/index'}}}
    mgr = PyPIManager(
        'https://mock',
        bucket='bucket',
        cache_list=[('cacheName', cache_info)],
        token='token',
        dryrun=False
    )

    pip_config_io = mock_open().__enter__.return_value = AnyIO()

    mgr.use()

    pip_config = pip_config_io.getvalue()

    assert 'index-url = https://token:token@mock/cache/cacheName/index' in pip_config
    assert '.cache/stable.world/bucket-pypi' in pip_config


@patch('stable_world.managers.pypi.open')
def test_pypi_manager_pinned(mock_open):

    cache_info = {'url': 'http://pypi/', 'config': {'global': {'index-url': 'http://pypi/index'}}}
    mgr = PyPIManager(
        'https://mock',
        bucket='bucket',
        cache_list=[('cacheName', cache_info)],
        token='token',
        dryrun=False
    )

    pip_config_io = mock_open().__enter__.return_value = AnyIO()

    mgr.use()

    pip_config = pip_config_io.getvalue()

    assert 'index-url = https://token:token@mock/cache/cacheName/index' in pip_config
    assert '.cache/stable.world/bucket-pypi' in pip_config

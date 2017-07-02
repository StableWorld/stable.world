from __future__ import unicode_literals

from mock import patch
import six
from stable_world.managers.pypi import PyPIManager


@patch('stable_world.managers.pypi.open')
def test_pypi_manager(mock_open):

    cache_info = {'url': 'http://pypi/', 'config': {'global': {'index-url': 'http://pypi/index'}}}
    mgr = PyPIManager(
        'https://mock',
        urls={'pypi': cache_info},
        bucket='bucket',
        token='MockToken',
        dryrun=False
    )

    pip_config_io = mock_open().__enter__.return_value = six.StringIO()

    mgr.use()

    pip_config = pip_config_io.getvalue()

    assert 'index-url = https://token:MockToken@mock/cache/bucket/pypi/index' in pip_config
    assert '.cache/stable.world/bucket' in pip_config

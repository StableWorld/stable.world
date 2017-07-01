import mock
import io
from stable_world.script import configure
from fixture import CLITest
from click.testing import CliRunner


class Test(CLITest):

    @mock.patch('stable_world.managers.pypi.open')
    def test_configure_pip(self, pypi_open):
        obj = self.application_mock()
        obj.token = 'chicken'

        obj.client.bucket.return_value = {'bucket': {
            'name': 'bucket11',
            'frozen': False,
            'urls': {'pypi': {
                'url': 'http://pypi.python.org',
                'config': {'global': {'index-url': 'http://pypi.python.org'}}
            }}
        }}

        config_file = io.StringIO()
        config_file.close = lambda: None
        pypi_open.return_value = config_file

        result = CliRunner().invoke(
            configure, [
                '--bucket', 'bucket11',
                'pip',
            ],
            obj=obj
        )

        self.assert_success(result)

        assert 'Writing pip config file' in result.output

        configvalue = config_file.getvalue()
        assert 'index-url = //token:chicken@/mockURL/cache/pypi/' in configvalue
        assert 'cache-dir = ' in configvalue
        assert '/stable.world/bucket11' in configvalue

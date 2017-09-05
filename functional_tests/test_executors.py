import mock

from stable_world.commands.execute import pip, npm, curl

from fixture import CLITest
from click.testing import CliRunner


class Test(CLITest):

    @mock.patch('stable_world.executors.check_call')
    def test_pip(self, check_call):
        obj = self.application_mock()

        obj.client.get_cache_url.return_value = 'http://cache_url/cache/'

        result = CliRunner().invoke(
            pip, [
                '--token', 't1', '--email', 'adsf',
                '-b', 'bl11', 'install', 'flarg', '--unknown-option'
            ],
            obj=obj
        )
        print(result.output)

        if result.exception:
            raise result.exception

        assert result.exit_code == 0

        args = check_call.call_args_list[0][0]
        kwargs = check_call.call_args_list[0][1]
        assert args[0][1:] == ['install', 'flarg', '--unknown-option']
        assert args[0][0].endswith('pip')
        assert 'PIP_INDEX_URL' in kwargs['env']
        assert kwargs['env']['PIP_INDEX_URL'] == 'http://token:t1@cache_url/cache/bl11/pypi/simple/'

        assert 'PIP_CACHE_DIR' in kwargs['env']
        assert kwargs['env']['PIP_CACHE_DIR'].endswith('.cache/stable.world/bl11')

    @mock.patch('stable_world.executors.check_call')
    def test_npm(self, check_call):
        obj = self.application_mock()

        obj.client.get_cache_url.return_value = 'http://cache_url/cache/'

        result = CliRunner().invoke(
            npm, [
                '--token', 't1', '--email', 'adsf',
                '-b', 'buck3t', 'install', 'flarg'
            ],
            obj=obj
        )
        print(result.output)

        if result.exception:
            raise result.exception

        assert result.exit_code == 0

        args = check_call.call_args_list[0][0]
        kwargs = check_call.call_args_list[0][1]
        assert args[0][1:] == ['install', 'flarg']
        assert args[0][0].endswith('npm')
        assert 'NPM_CONFIG_USERCONFIG' in kwargs['env']
        assert kwargs['env']['NPM_CONFIG_USERCONFIG'].endswith('.npmrc')

        # TODO: test config file values

    @mock.patch('stable_world.executors.check_call')
    def test_curl(self, check_call):
        obj = self.application_mock()

        obj.client.get_cache_url.return_value = 'http://cache_url/cache/'

        result = CliRunner().invoke(
            curl, [
                '--token', 't1', '--email', 'adsf',
                '-b', 'buck3t', 'http://httpbin.org/get'
            ],
            obj=obj
        )
        print(result.output)

        if result.exception:
            raise result.exception

        assert result.exit_code == 0

        args = check_call.call_args_list[0][0]
        assert args[0][1:] == ['http://token:t1@cache_url/cache/buck3t/-/http://httpbin.org/get']
        assert args[0][0].endswith('curl')

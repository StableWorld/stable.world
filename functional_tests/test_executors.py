import mock

from stable_world.script import pip
from fixture import CLITest
from click.testing import CliRunner


class Test(CLITest):

    @mock.patch('stable_world.executors.check_call')
    def test_pip(self, check_call):
        obj = self.application_mock()

        result = CliRunner().invoke(
            pip, [
                '--token', 't1', '--email', 'adsf',
                '-b', 'bl11', 'install', 'flarg', '--unknown-option'
            ],
            obj=obj
        )
        print(result.output)
        assert result.exit_code == 0

        args = check_call.call_args_list[0][0]
        kwargs = check_call.call_args_list[0][1]
        assert args[0] == ['pip', 'install', 'flarg', '--unknown-option']
        assert 'PIP_INDEX_URL' in kwargs['env']
        assert kwargs['env']['PIP_INDEX_URL'] == 'mockURL/cache/bl11/pypi/simple/'

        assert 'PIP_CACHE_DIR' in kwargs['env']
        assert kwargs['env']['PIP_CACHE_DIR'] == '~/.cache/stable.world/bl11'
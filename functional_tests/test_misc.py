from stable_world.commands.misc import set as set_config
from fixture import CLITest
from click.testing import CliRunner


class Test(CLITest):

    def test_set(self):
        obj = self.application_mock()

        result = CliRunner().invoke(
            set_config, ['someKey', 'someValue'],
            obj=obj
        )
        print(result.output)
        if result.exception:
            raise result.exception

        assert result.exit_code == 0

        assert obj.write_config.called

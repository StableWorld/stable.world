from stable_world.script import set as set_config
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
        assert result.exit_code == 0

        assert obj.write_config.called

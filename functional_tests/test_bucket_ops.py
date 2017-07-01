import mock
from click.testing import CliRunner
from stable_world import application
from stable_world.script import main
from fixture import CLITest


class Test(CLITest):

    def setUp(self):
        self.OGApp = application.StableWorldApplication
        application.StableWorldApplication = mock.Mock

    def tearDown(self):
        application.StableWorldApplication = self.OGApp

    def test_freeze(self):
        obj = self.application_mock()

        result = CliRunner().invoke(
            main, ['--email', 'email', '--token', 'token', 'bucket:freeze', 'b1'],
            obj=obj
        )
        assert 'Success: Bucket b1 frozen' in result.output
        assert result.exit_code == 0

    def test_unfreeze(self):
        obj = self.application_mock()

        result = CliRunner().invoke(
            main, ['--email', 'email', '--token', 'token', 'bucket:unfreeze', 'b1'],
            obj=obj
        )
        assert 'Success: Unfroze Bucket b1' in result.output
        assert result.exit_code == 0

    def test_destroy(self):

        obj = self.application_mock()
        result = CliRunner().invoke(
            main,
            ['bucket:destroy', 'far-shoehorn', '--token=token', '--email=email'],
            obj=obj
        )

        if result.exception:
            raise result.exception
        assert result.exit_code == 0

        obj.client.delete_bucket.assert_called_with('far-shoehorn')

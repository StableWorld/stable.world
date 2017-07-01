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

    def test_bucket(self):
        obj = self.application_mock()

        obj.client.bucket.return_value = {'bucket': {
            'frozen': True,
            'name': 'b1u3',
            'urls': {}
        }}

        result = CliRunner().invoke(
            main, ['--email', 'email', '--token', 'token', 'bucket', 'b1u3'],
            obj=obj
        )
        assert 'bucket: b1u3[frozen]' in result.output
        assert result.exit_code == 0

    def test_create(self):
        obj = self.application_mock()

        obj.client.add_bucket.return_value = {'bucket': {
            'frozen': False,
            'name': 'new_bucket',
            'urls': {}
        }}

        result = CliRunner().invoke(
            main, ['--email', 'email', '--token', 'token', 'bucket:create', 'new_bucket'],
            obj=obj
        )
        assert 'bucket: new_bucket' in result.output
        assert result.exit_code == 0

    def test_list(self):
        obj = self.application_mock()

        obj.client.buckets.return_value = [{
            'frozen': False,
            'name': 'b1',
            'urls': {}
        }, {
            'frozen': False,
            'name': 'b2',
            'urls': {}
        }]

        result = CliRunner().invoke(
            main, ['--email', 'email', '--token', 'token', 'bucket:list'],
            obj=obj
        )
        assert '+ b1' in result.output
        assert '+ b2' in result.output
        assert result.exit_code == 0

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

    def test_rollback(self):
        obj = self.application_mock()

        obj.client.rollback.return_value = {'ok': True}

        result = CliRunner().invoke(
            main, ['--email', 'email', '--token', 'token', 'bucket:rollback', 'b1', '--when', '2012/12/12'],
            obj=obj
        )
        assert 'Success: Bucket b1 rolled back to Wed Dec 12 00:00:00 2012' in result.output
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

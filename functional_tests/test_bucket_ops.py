import unittest
import mock
from click.testing import CliRunner
from stable_world import errors, application
from stable_world.script import main


def application_mock():
    app = mock.Mock()
    app.client.site = 'mockURL'
    app.config = {'url': 'mockURL'}
    options = {}

    def update_config_from_options():
        app.token = options.get('token')
        app.email = options.get('email')
        app.config.update(options)

    def update_option(name, value):
        options[name] = value

    app.token = None
    app.email = None
    app.password = None
    app.update_option = update_option
    app.update_config_from_options = update_config_from_options
    return app


class Test(unittest.TestCase):

    def setUp(self):
        self.OGApp = application.StableWorldApplication
        application.StableWorldApplication = mock.Mock

    def tearDown(self):
        application.StableWorldApplication = self.OGApp

    def test_freeze(self):
        obj = application_mock()

        obj.client.token.return_value = 'myToken'
        obj.email = 'fake-email'
        obj.token = 'fake-token'

        result = CliRunner().invoke(
            main, ['--email', 'email', '--password', 'password', 'bucket:freeze', '--bucket', 'b1'],
            obj=obj
        )
        print(result.output)
        assert result.exit_code == 0

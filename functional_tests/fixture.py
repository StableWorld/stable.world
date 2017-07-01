import unittest
import mock
import six
from stable_world import application


class CLITest(unittest.TestCase):

    def setUp(self):
        self.OGApp = application.StableWorldApplication
        application.StableWorldApplication = mock.Mock

    def tearDown(self):
        application.StableWorldApplication = self.OGApp

    def application_mock(self):
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

    def assert_success(self, result):
        print(result.output)

        if result.exc_info:
            try:
                six.reraise(*result.exc_info)
            except SystemExit:
                pass

        assert result.exit_code == 0

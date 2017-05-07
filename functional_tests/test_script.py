import unittest
import mock
import requests_mock
from click.testing import CliRunner
from stable_world import errors, application
from stable_world.script import main


def application_mock():
    app = mock.Mock()
    app.client.site_url = 'mockURL'
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
        # self.patch = mock.patch('stable_world.application.StableWorldApplication', autospec=True)
        # self.AppClass = self.patch.start()s
        # tempfile.gettempdir()
        # self.orig_cache_dirname = config.cache_dirname
        # self.orig_config_filename = config.config_filename
        # tmp = tempfile.mkdtemp()
        # config.cache_dirname = os.path.join(tmp, 'cache')
        # config.config_filename = os.path.join(tmp, 'config/test-config.ini')

        # config2.make_dirs()

        # self.default_config = dict(config.default_config)
        # config.default_config.clear()
        # config.default_config.update({'url': 'http://mock'})
        # config.config.clear()
        # config.config.update(config.default_config)

        self.requests_patch = requests_mock.mock()
        self.requests = self.requests_patch.start()

        # self.update_config_file_patch = mock.patch('stable_world.config.update_config_file')
        # self.update_config_file = self.update_config_file_patch.start()

        # self.update_netrc_file_patch = mock.patch('stable_world.config.update_netrc_file')
        # self.update_netrc_file = self.update_netrc_file_patch.start()
        pass

    def tearDown(self):
        application.StableWorldApplication = self.OGApp
        # self.patch.stop()
        self.requests_patch.stop()

        # self.update_config_file_patch.stop()
        # self.update_netrc_file_patch.stop()
        #
        # config.cache_dirname = self.orig_cache_dirname
        # config.config_filename = self.orig_config_filename
        #
        # config.default_config.clear()
        # config.default_config.update(self.default_config)
        # config.config.clear()
        # config.config.update(config.default_config)

    @mock.patch('stable_world.interact.setup_project.ProjectConfigurator')
    def test_main(self, ProjectConfigurator):

        runner = CliRunner()

        obj = application_mock()

        # User exists
        obj.client.token.return_value = 'myToken'

        result = runner.invoke(main, ['--token=', '--email='], input='email\npassword\n', obj=obj)

        if result.exception:
            raise result.exception

        assert result.exit_code == 0

        obj.client.token.assert_called_with('email', 'password', scopes={'api': 'write'})
        obj.update_netrc.assert_called_with('email', 'myToken')

        ProjectConfigurator.detect().setup.assert_called()
        ProjectConfigurator.detect().setup_project_name.assert_called()
        ProjectConfigurator.detect().setup_project_env.assert_called()
        ProjectConfigurator.detect().setup_project_ci.assert_called()

    def test_destroy(self):

        obj = application_mock()
        # obj.email = 'email'
        # obj.token = 'myToken'
        result = CliRunner().invoke(
            main,
            ['project:destroy', '-p', 'far-shoehorn', '--token=token', '--email=email'],
            obj=obj
        )

        if result.exception:
            raise result.exception
        assert result.exit_code == 0

        obj.client.delete_project.assert_called_with('far-shoehorn')

    def test_login(self):

        obj = application_mock()
        obj.client.token.return_value = 'myToken'

        result = CliRunner().invoke(
            main, ['login'],
            input='email\npassword\n',
            obj=obj
        )
        if result.exception:
            raise result.exception
        assert result.exit_code == 0

        obj.client.token.assert_called_with('email', 'password', scopes={'api': 'write'})
        obj.update_netrc.assert_called_with('email', 'myToken')

    def test_login_user_does_not_exist(self):

        obj = application_mock()
        obj.client.token.side_effect = errors.NotFound('')

        result = CliRunner().invoke(
            main, ['login'],
            input='email\npassword\n',
            obj=obj
        )
        assert isinstance(result.exception, errors.NotFound)
        assert result.exit_code != 0

        obj.update_netrc.assert_not_called()

    def test_register(self):

        obj = application_mock()
        obj.client.token.side_effect = errors.NotFound('')
        obj.client.register.return_value = 'myToken'

        result = CliRunner().invoke(
            main, ['register'],
            input='email\npassword\npassword\n',
            obj=obj
        )
        if result.exception:
            raise result.exception
        assert result.exit_code == 0

        obj.client.register.assert_called_with('email', 'password')
        obj.update_netrc.assert_called_with('email', 'myToken')

    def test_register_wrong_confirm_password(self):

        obj = application_mock()
        obj.client.token.side_effect = errors.NotFound('')
        obj.client.register.return_value = 'myToken'

        result = CliRunner().invoke(
            main, ['register'],
            input='email\npassword\nwrongPassword\n',
            obj=obj
        )
        assert isinstance(result.exception, errors.UserError)
        assert result.exit_code != 0

    @mock.patch('stable_world.managers.use')
    def test_use(self, use):

        urls = {
            "conda": {
                "config": {
                    "channel": "https://repo.continuum.io/pkgs/free/"
                },
                "type": "conda",
                "url": "https://repo.continuum.io/"
            },
            "pypi": {
                "config": {
                    "global": {
                        "index-url": "https://pypi.python.org/simple/"
                    }
                },
                "type": "pypi",
                "url": "https://pypi.python.org/"
            }
        }

        # self.requests_patch.get('http://mock/api/projects/test-project',
        #     json={'project': {'pinned_to': None, 'urls': urls}}
        # )
        # self.requests_patch.post('http://mock/api/tags/test-project/create-tag',
        #     json={}
        # )

        use.return_value = {}

        obj = application_mock()
        # User exists
        obj.client.token.return_value = 'myToken'
        obj.get_using.return_value = None
        obj.client.project.return_value = {'project': {'pinned_to': None, 'urls': urls}}
        result = CliRunner().invoke(
            main, [
                'use', '-p', 'test-project', '-t', 'create-tag',
                '--email', 'email', '--token', 'myToken'
            ],
            obj=obj
        )
        if result.exception:
            raise result.exception
        assert result.exit_code == 0

        self.assertEqual(use.call_count, 2)
        self.assertEqual(
            use.call_args_list[0][0],
            (
                'mockURL', 'conda', 'test-project',
                [('conda', {
                    'config': {'channel': 'https://repo.continuum.io/pkgs/free/'},
                    'type': 'conda', 'url': 'https://repo.continuum.io/'
                })],
                'myToken',
                False
            )
        )

        self.assertEqual(
            use.call_args_list[1][0],
            (
                'mockURL', 'pypi', 'test-project',
                [('pypi', {
                    'config': {'global': {'index-url': 'https://pypi.python.org/simple/'}},
                    'type': 'pypi', 'url': 'https://pypi.python.org/'
                })],
                'myToken',
                False
            )
        )


if __name__ == "__main__":
    unittest.main()

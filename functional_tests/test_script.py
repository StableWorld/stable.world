import unittest
import mock
import requests_mock
from stable_world.config import default_config, config
from click.testing import CliRunner
from stable_world.script import main


class Test(unittest.TestCase):

    def setUp(self):
        self.default_config = dict(default_config)
        default_config.clear()
        default_config.update({'url': 'http://mock'})
        config.clear()
        config.update(default_config)
        self.requests_patch = requests_mock.mock()
        self.requests = self.requests_patch.start()

        self.update_config_file_patch = mock.patch('stable_world.config.update_config_file')
        self.update_config_file = self.update_config_file_patch.start()

        self.update_netrc_file_patch = mock.patch('stable_world.config.update_netrc_file')
        self.update_netrc_file = self.update_netrc_file_patch.start()

    def tearDown(self):
        self.requests_patch.stop()
        self.update_config_file_patch.stop()
        self.update_netrc_file_patch.stop()

        default_config.clear()
        default_config.update(self.default_config)
        config.clear()
        config.update(default_config)

    @mock.patch('stable_world.interact.setup_project.random_project_name')
    def test_main(self, random_project_name):

        random_project_name.return_value = 'test-project'
        runner = CliRunner()

        self.requests_patch.post('http://mock/api/account/login_or_register', json={'token': 'mockToken'})
        self.requests_patch.post('http://mock/api/projects/test-project', json={})

        result = runner.invoke(main, ['--token=', '--email='], input='email\npassword\n')

        if result.exception:
            raise result.exception

        assert result.exit_code == 0

        history = self.requests_patch.request_history

        self.assertEqual(history[0].url, 'http://mock/api/account/login_or_register')
        self.assertEqual(history[0].json(), {'email': 'email', 'password': 'password'})

        self.assertEqual(self.update_config_file.call_args, None)
        self.assertEqual(
            self.update_netrc_file.call_args[1],
            {'email': 'email', 'token': 'mockToken'}
        )

        self.assertEqual(history[1].url, 'http://mock/api/projects/test-project')

    def test_destroy(self):

        self.requests_patch.delete('http://mock/api/projects/far-shoehorn', json={'ok': True})

        result = CliRunner().invoke(
            main,
            ['project:destroy', '-p', 'far-shoehorn', '--token=token', '--email=email']
        )
        if result.exception:
            raise result.exception

        assert result.exit_code == 0

        history = self.requests_patch.request_history
        self.assertIn('Project far-shoehorn removed', result.output)
        self.assertEqual(history[0].url, 'http://mock/api/projects/far-shoehorn')

    def test_login(self):

        self.requests_patch.post('http://mock/api/account/login_or_register', json={'token': 'mockToken'})

        result = CliRunner().invoke(
            main, ['login'],
            input='email\npassword\n'
        )
        if result.exception:
            raise result.exception
        assert result.exit_code == 0

        history = self.requests_patch.request_history

        self.assertEqual(history[0].url, 'http://mock/api/account/login_or_register')
        self.assertEqual(history[0].json(), {'email': 'email', 'password': 'password'})

        self.assertEqual(self.update_netrc_file.call_args[1], {'email': 'email', 'token': 'mockToken'})

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

        self.requests_patch.get('http://mock/api/projects/test-project',
            json={'project': {'pinned_to': None, 'urls': urls}}
        )
        self.requests_patch.post('http://mock/api/tags/test-project/create-tag',
            json={}
        )

        result = CliRunner().invoke(
            main, [
                'use', '-p', 'test-project', '-t', 'create-tag',
                '--email', 'email', '--token', 'myToken'
            ],
        )
        if result.exception:
            raise result.exception
        assert result.exit_code == 0

        self.assertEqual(self.update_netrc_file.call_args[1], {'email': 'email', 'token': 'myToken'})

        history = self.requests_patch.request_history

        self.assertEqual(history[0].url, 'http://mock/api/projects/test-project')
        self.assertEqual(history[1].url, 'http://mock/api/tags/test-project/create-tag')

        self.assertEqual(use.call_count, 2)
        self.assertEqual(
            use.call_args_list[0][0],
            (
                'conda', 'test-project', 'create-tag',
                [('conda', {
                    'config': {'channel': 'https://repo.continuum.io/pkgs/free/'},
                    'type': 'conda', 'url': 'https://repo.continuum.io/'
                })],
                None, False
            )
        )

        self.assertEqual(
            use.call_args_list[1][0],
            (
                'pypi', 'test-project', 'create-tag',
                [('pypi', {
                    'config': {'global': {'index-url': 'https://pypi.python.org/simple/'}},
                    'type': 'pypi', 'url': 'https://pypi.python.org/'
                })],
                None, False
            )
        )


if __name__ == "__main__":
    unittest.main()

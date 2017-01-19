import unittest
import mock
import requests_mock
from stable_world.config import config
from click.testing import CliRunner
from stable_world.script import main


class Test(unittest.TestCase):

    def setUp(self):
        config.clear()
        config.update({'url': 'http://mock/'})
        self.requests_patch = requests_mock.mock()
        self.requests = self.requests_patch.start()

        self.yaml_patch = mock.patch('yaml.safe_dump')
        self.yaml_safe_dump = self.yaml_patch.start()

    def tearDown(self):
        self.requests_patch.stop()
        self.yaml_patch.stop()

    @mock.patch('stable_world.interact.setup_space.random_project_name')
    def test_main(self, random_project_name):

        random_project_name.return_value = 'test-project'
        runner = CliRunner()

        self.requests_patch.post('http://mock//account/login_or_register', json={'token': 'mockToken'})
        self.requests_patch.post('http://mock//spaces/test-project', json={})

        result = runner.invoke(main, ['--token=', '--email='], input='email\npassword\n')

        if result.exception:
            raise result.exception

        assert result.exit_code == 0

        history = self.requests_patch.request_history

        self.assertEqual(history[0].url, 'http://mock//account/login_or_register')
        self.assertEqual(history[0].json(), {'email': 'email', 'password': 'password'})

        self.assertEqual(
            self.yaml_safe_dump.call_args[0][0],
            {'url': 'http://mock/', 'email': 'email', 'token': 'mockToken'}
        )

        self.assertEqual(history[1].url, 'http://mock//spaces/test-project')

    def test_destroy(self):

        self.requests_patch.delete('http://mock//spaces/far-shoehorn', json={'ok': True})

        result = CliRunner().invoke(
            main,
            ['project:destroy', '-p', 'far-shoehorn', '--token=token', '--email=email']
        )
        if result.exception:
            raise result.exception

        assert result.exit_code == 0

        history = self.requests_patch.request_history
        self.assertIn('Project far-shoehorn removed', result.output)
        self.assertEqual(history[0].url, 'http://mock//spaces/far-shoehorn')


if __name__ == "__main__":
    unittest.main()

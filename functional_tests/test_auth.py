import unittest
from click.testing import CliRunner
from stable_world import errors
from stable_world.script import main
from fixture import CLITest


class Test(CLITest):

    def test_main(self):

        runner = CliRunner()

        obj = self.application_mock()

        # User exists
        obj.client.token.return_value = 'myToken'

        result = runner.invoke(main, ['--token=', '--email='], input='email\npassword\n', obj=obj)

        if result.exception:
            raise result.exception

        assert result.exit_code == 0

        obj.client.token.assert_called_with('email', 'password', scopes=['api', 'bucket'])
        obj.update_netrc.assert_called_with('email', 'myToken')

    def test_login(self):

        obj = self.application_mock()
        obj.client.token.return_value = 'myToken'

        result = CliRunner().invoke(
            main, ['login'],
            input='email\npassword\n',
            obj=obj
        )
        if result.exception:
            raise result.exception
        assert result.exit_code == 0

        obj.client.token.assert_called_with('email', 'password', scopes=['api', 'bucket'])
        obj.update_netrc.assert_called_with('email', 'myToken')

    def test_login_user_does_not_exist(self):

        obj = self.application_mock()
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

        obj = self.application_mock()
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

        obj.client.register.assert_called_with('email', 'password', scopes=['api', 'bucket'])
        obj.update_netrc.assert_called_with('email', 'myToken')

    def test_register_wrong_confirm_password(self):

        obj = self.application_mock()
        obj.client.token.side_effect = errors.NotFound('')
        obj.client.register.return_value = 'myToken'

        result = CliRunner().invoke(
            main, ['register'],
            input='email\npassword\nwrongPassword\n',
            obj=obj
        )
        assert isinstance(result.exception, errors.UserError)
        assert result.exit_code != 0


if __name__ == "__main__":
    unittest.main()

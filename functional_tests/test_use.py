# import unittest
# import mock
# from click.testing import CliRunner
# from stable_world.script import main
# from fixture import CLITest
#
#
# class Test(CLITest):
#
#     @mock.patch('stable_world.managers.use')
#     def test_use(self, use):
#
#         urls = {
#             "conda": {
#                 "config": {
#                     "channel": "https://repo.continuum.io/pkgs/free/"
#                 },
#                 "type": "conda",
#                 "url": "https://repo.continuum.io/"
#             },
#             "pypi": {
#                 "config": {
#                     "global": {
#                         "index-url": "https://pypi.python.org/simple/"
#                     }
#                 },
#                 "type": "pypi",
#                 "url": "https://pypi.python.org/"
#             }
#         }
#
#         use.return_value = {}
#
#         obj = self.application_mock()
#         # User exists
#         obj.client.token.return_value = 'myToken'
#         obj.get_using.return_value = None
#         obj.client.bucket.return_value = {'bucket': {'urls': urls, 'frozen': False}}
#         result = CliRunner().invoke(
#             main, [
#                 'use', 'test-bucket',
#                 '--email', 'email', '--token', 'myToken'
#             ],
#             obj=obj
#         )
#         if result.exception:
#             raise result.exception
#         assert result.exit_code == 0
#
#         self.assertEqual(use.call_count, 2)
#         self.assertEqual(
#             use.call_args_list[0][0],
#             (
#                 'mockURL', 'conda', 'test-bucket',
#                 [('conda', {
#                     'config': {'channel': 'https://repo.continuum.io/pkgs/free/'},
#                     'type': 'conda', 'url': 'https://repo.continuum.io/'
#                 })],
#                 'myToken',
#                 False
#             )
#         )
#
#         self.assertEqual(
#             use.call_args_list[1][0],
#             (
#                 'mockURL', 'pypi', 'test-bucket',
#                 [('pypi', {
#                     'config': {'global': {'index-url': 'https://pypi.python.org/simple/'}},
#                     'type': 'pypi', 'url': 'https://pypi.python.org/'
#                 })],
#                 'myToken',
#                 False
#             )
#         )
#
#
# if __name__ == "__main__":
#     unittest.main()

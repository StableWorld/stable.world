import unittest
from stable_world import config

example = '''
machine api.heroku.com
    login test@gmail.com
    password someGreatToken1
machine git.heroku.com
    login test@gmail.com
    password someGreatToken2
machine surge.surge.sh
    login test@gmail.com
    password someGreatToken3
'''


class Test(unittest.TestCase):

    def test_remove_machine_no_match(self):

        result = config.remove_machine('host', example)
        self.assertEqual(result, example)

    def test_remove_machine_start(self):

        expected = '''
machine git.heroku.com
    login test@gmail.com
    password someGreatToken2
machine surge.surge.sh
    login test@gmail.com
    password someGreatToken3
'''
        result = config.remove_machine('api.heroku.com', example)
        self.assertEqual(result, expected)

    def test_remove_machine_middle(self):

        expected = '''
machine api.heroku.com
    login test@gmail.com
    password someGreatToken1
machine surge.surge.sh
    login test@gmail.com
    password someGreatToken3
'''
        result = config.remove_machine('git.heroku.com', example)
        self.assertEqual(result, expected)

    def test_remove_machine_end(self):

        expected = '''
machine api.heroku.com
    login test@gmail.com
    password someGreatToken1
machine git.heroku.com
    login test@gmail.com
    password someGreatToken2
'''
        result = config.remove_machine('surge.surge.sh', example)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()

from stable_world.interact.project_configs.default import CustomProjectHelper
from mock import Mock
import unittest


class Test(unittest.TestCase):

    def test_default(self):

        client = Mock()
        config = CustomProjectHelper(client, '.')

        config.setup()
        print('ji')

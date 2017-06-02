from stable_world.interact.bucket_configs.default import CustomBucketHelper
from mock import Mock
import unittest


class Test(unittest.TestCase):

    def test_default(self):

        client = Mock()
        config = CustomBucketHelper(client, '.')

        config.setup()
        print('ji')

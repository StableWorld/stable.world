
from .base import BucketConfigurator
from .circleci import CircleBucketHelper
from .default import CustomBucketHelper

BucketConfigurator.register('circleci', CircleBucketHelper)
BucketConfigurator.register('custom', CustomBucketHelper)

BucketConfigurator.default('custom')

__all__ = ('BucketConfigurator', )

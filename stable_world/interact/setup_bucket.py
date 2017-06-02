
from .bucket_configs import BucketConfigurator


def setup_bucket(app, working_dir, ty=None):

    if ty:
        bucket_config = BucketConfigurator.get(ty, app, working_dir)
    else:
        bucket_config = BucketConfigurator.detect(app, working_dir)

    bucket_config.setup()

    bucket_config.setup_bucket_name()
    bucket_config.setup_bucket_env()
    bucket_config.setup_bucket_ci()

    bucket_config.success()

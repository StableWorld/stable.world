import sys
import os
from subprocess import check_call


def execute_pip(app, bucket, pip_args):
    token = app.token
    app.client.check_bucket_token(bucket, token)
    args = ['pip'] + list(pip_args)

    env = os.environ.copy()

    env['PIP_INDEX_URL'] = '{url}/cache/{bucket}/pypi/simple/'.format(
        url=app.config['url'], bucket=bucket,
    )

    env['PIP_CACHE_DIR'] = os.path.join('~', '.cache', 'stable.world', bucket)

    if not os.path.isdir(env['PIP_CACHE_DIR']):
        os.makedirs(env['PIP_CACHE_DIR'])

    check_call(args, stdout=sys.stdout, stderr=sys.stderr, env=env)

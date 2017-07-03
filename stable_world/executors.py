import sys
import os
from stable_world import errors
from subprocess import check_call, CalledProcessError
from logging import getLogger

logger = getLogger(__name__)


def execute_pip(app, bucket_name, pip_args):
    token = app.token
    app.client.check_bucket_token(bucket_name, token)
    args = ['pip'] + list(pip_args)

    env = os.environ.copy()

    env['PIP_INDEX_URL'] = '{url}/cache/{bucket}/pypi/simple/'.format(
        url=app.config['url'], bucket=bucket_name,
    )
    logger.debug('Set envvar PIP_INDEX_URL={}'.format(env['PIP_INDEX_URL']))

    PIP_CACHE_DIR = os.path.join('~', '.cache', 'stable.world', bucket_name)
    env['PIP_CACHE_DIR'] = os.path.expanduser(PIP_CACHE_DIR)
    logger.debug('Set envvar PIP_CACHE_DIR={}'.format(env['PIP_CACHE_DIR']))

    if not os.path.isdir(env['PIP_CACHE_DIR']):
        os.makedirs(env['PIP_CACHE_DIR'])

    logger.debug('Executing {}'.format(' '.join(args)))
    print("call")
    try:
        check_call(args, stdout=sys.stdout, stderr=sys.stderr, env=env)
    except CalledProcessError:
        # User friendly error
        raise errors.UserError("Command pip failed")

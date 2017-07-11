from __future__ import print_function, unicode_literals, absolute_import

import sys
import os
from base64 import b64encode
from tempfile import mktemp
from subprocess import check_call, CalledProcessError
from logging import getLogger
from contextlib import contextmanager

from stable_world import errors

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
    try:
        check_call(args, stdout=sys.stdout, stderr=sys.stderr, env=env)
    except OSError as err:
        if err.errno == 2:
            raise errors.UserError(
                "Could not execute the command 'pip'. "
                "please check that pip is installed"
            )
        else:
            raise
    except CalledProcessError:
        # User friendly error
        raise errors.UserError("Command pip failed")


def write_npm_config(fd, obj):
    for key, value in obj.items():
        print(key, value, sep='=', file=fd)
    return


@contextmanager
def remove_file(filename):
    try:
        yield
    finally:
        try:
            os.unlink(filename)
        except:
            pass


def execute_npm(app, bucket_name, npm_args):

    token = app.token
    app.client.check_bucket_token(bucket_name, token)
    args = ['npm'] + list(npm_args)

    env = os.environ.copy()
    env['NPM_CONFIG_USERCONFIG'] = mktemp(prefix='npm', suffix='config')

    logger.debug('set envvar NPM_CONFIG_USERCONFIG={NPM_CONFIG_USERCONFIG}'.format(**env))

    with remove_file(env['NPM_CONFIG_USERCONFIG']):
        npm_config = {}
        npm_config['always-auth'] = 'true'
        npm_config['registry'] = '{url}/cache/{bucket}/npm/'.format(
            url=app.config['url'], bucket=bucket_name,
        )
        # TODO: implement me
        npm_config['_auth'] = b64encode('token:{}'.format(token).encode()).decode()

        with open(env['NPM_CONFIG_USERCONFIG'], 'w') as fd:
            write_npm_config(fd, npm_config)

        logger.debug('Executing {}'.format(' '.join(args)))

        try:
            check_call(args, stdout=sys.stdout, stderr=sys.stderr, env=env)
        except CalledProcessError:
            # User friendly error
            raise errors.UserError("Command npm failed")

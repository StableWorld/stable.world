from __future__ import print_function, unicode_literals, absolute_import

import sys
import os
from tempfile import mktemp
from subprocess import check_call, CalledProcessError
from logging import getLogger
from contextlib import contextmanager
from six.moves.urllib_parse import urlparse
from stable_world.managers.npm import write_npm_config
from stable_world import errors

logger = getLogger(__name__)


def whereis(exe):
    'Find the pull path to executable, linux only'
    for path in os.environ['PATH'].split(os.pathsep):
        if os.path.isfile(os.path.join(path, exe)):
            return os.path.join(path, exe)
    return exe


CURL = whereis('curl')
NPM = whereis('npm')
PIP = whereis('pip')


def add_basic_auth(url, token):
    """
    Adds basic auth token to url eg

    http://stable.world => http://token:TOKEN@stable.world
    """
    parsed = urlparse(url)
    if '@' in parsed.netloc:
        _, netloc = parsed.netloc.split('@', 1)
    else:
        netloc = parsed.netloc

    netloc = 'token:{token}@{netloc}'.format(token=token, netloc=netloc)
    parsed = parsed._replace(netloc=netloc)
    return parsed.geturl()


def safe_call(args, env):
    """
    Run subprocess.check_call and provide nice error messages on failure
    """

    logger.debug('Executing {}'.format(' '.join(args)))
    try:
        check_call(args, stdout=sys.stdout, stderr=sys.stderr, env=env)
    except OSError as err:
        if err.errno == 2:
            msg = (
                "Could not execute the command '{0}'. "
                "please check that {0} is installed"
            ).format(args[0])
            raise errors.UserError(msg)
        else:
            raise
    except CalledProcessError:
        # User friendly error
        raise errors.UserError("Command {} failed".format(args[0]))


def execute_pip(app, bucket_name, pip_args):
    token = app.token
    app.client.check_bucket_token(bucket_name, token)
    cache_url = add_basic_auth(app.client.get_cache_url(), token)
    args = [PIP] + list(pip_args)

    env = os.environ.copy()

    pip_index_url = '{url}{bucket}/pypi/simple/'.format(
        url=cache_url, bucket=bucket_name,
    )
    env['PIP_INDEX_URL'] = pip_index_url
    logger.debug('Set envvar PIP_INDEX_URL={}'.format(env['PIP_INDEX_URL']))

    PIP_CACHE_DIR = os.path.join('~', '.cache', 'stable.world', bucket_name)
    env['PIP_CACHE_DIR'] = os.path.expanduser(PIP_CACHE_DIR)
    logger.debug('Set envvar PIP_CACHE_DIR={}'.format(env['PIP_CACHE_DIR']))

    if not os.path.isdir(env['PIP_CACHE_DIR']):
        os.makedirs(env['PIP_CACHE_DIR'])

    safe_call(args, env)


def execute_curl(app, bucket_name, curl_args):
    token = app.token
    app.client.check_bucket_token(bucket_name, token)
    cache_url = add_basic_auth(app.client.get_cache_url(), token)
    args = [CURL] + list(curl_args)

    if not urlparse(args[-1]).netloc:
        raise errors.UserError(
            "stable.world curl url argument must be "
            "last and must start with http(s)://"
        )

    env = os.environ.copy()

    args[-1] = '{url}{bucket}/-/{path}'.format(
        url=cache_url, bucket=bucket_name, path=args[-1]
    )

    safe_call(args, env)


@contextmanager
def remove_file(filename):
    """
    remove a file regardless of any exception
    """
    try:
        yield
    finally:
        try:
            pass
            # os.unlink(filename)
        except Exception:
            pass


def execute_npm(app, bucket_name, npm_args):

    token = app.token
    app.client.check_bucket_token(bucket_name, token)
    cache_url = app.client.get_cache_url()
    args = [NPM] + list(npm_args)

    env = os.environ.copy()
    env['NPM_CONFIG_USERCONFIG'] = mktemp(suffix='.npmrc')

    logger.debug('set envvar NPM_CONFIG_USERCONFIG={NPM_CONFIG_USERCONFIG}'.format(**env))

    with remove_file(env['NPM_CONFIG_USERCONFIG']):
        registry = '{url}{bucket}/npm/'.format(
            url=cache_url, bucket=bucket_name,
        )

        with open(env['NPM_CONFIG_USERCONFIG'], 'w') as fd:
            write_npm_config(fd, registry, token)

        safe_call(args, env)

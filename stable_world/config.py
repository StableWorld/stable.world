import os
import re
import logging
import json
import certifi
from zipfile import ZipFile
from . import errors
from .env import env
from .py_helpers import ConfigParser, urlparse

from netrc import netrc

logger = logging.getLogger(__name__)


def abs_expand(path):
    return os.path.abspath(os.path.expanduser(path))


# TODO windows locations
CONFIG_SECTION = 'stable.world'

config_filename = abs_expand(env.STABLE_WORLD_CONFIG)
netrc_filename = abs_expand(os.path.join('~', '.netrc'))
cache_dirname = abs_expand(env.STABLE_WORLD_CACHE_DIR)


default_config = {
    'url': env.STABLE_WORLD_URL
}

config = default_config.copy()


def make_dirs():
    try:
        if not os.path.isdir(cache_dirname):
            os.makedirs(cache_dirname)
    except OSError:
        msg = "Could not create cache directory {}".format(cache_dirname)
        raise errors.UserError(msg)

    try:
        test_perm = os.path.join(cache_dirname, '.perm-check')
        with open(test_perm, 'a'):
            pass
        os.unlink(test_perm)
    except OSError:
        msg = "Do no have write perms for cache directory '{}'".format(cache_dirname)
        raise errors.UserError(msg)

    try:
        config_dirname = os.path.dirname(config_filename)
        if not os.path.isdir(config_dirname):
            os.makedirs(config_dirname)
    except OSError:
        msg = "Could not create config directory {}".format(config_dirname)
        raise errors.UserError(msg)


def load_config():

    if os.path.isfile(config_filename):
        logger.info("load config from %s" % (config_filename))
        parser = ConfigParser()
        with open(config_filename) as fd:
            parser.read_file(fd, config_filename)
            _config = parser._sections.get(CONFIG_SECTION, {})
            config.update(_config)

    else:
        logger.info("no config file %s" % (config_filename))
        config.update(default_config)


def update_config_with_env():
    verify_https = env.STABLE_WORLD_VERIFY_HTTPS

    if verify_https in ['no', 'off']:
        verify_https = False
    if verify_https is None:
        verify_https = os.path.join(cache_dirname, 'cacert.pem')

    config.update(verify_https=verify_https)


def load_netrc():

    HOST = urlparse(config['url']).netloc.split(':', 1)[0]
    if os.path.isfile(netrc_filename):
        logger.info("load netrc host %s from %s" % (HOST, netrc_filename))
        EMAIL, _, TOKEN = netrc(netrc_filename).authenticators(HOST) or (None, None, None)
        config.update({'email': EMAIL, 'token': TOKEN})
    else:
        logger.info("netrc file %s does not exist" % (netrc_filename))


netrc_template = '''
machine %(host)s
    login %(email)s
    password %(token)s
'''


def remove_machine(machine, netrc_content):
    lines = netrc_content.split('\n')
    modified = []
    logger.info("Remove machine %s", machine)
    in_machine_context = False

    macine_re = re.compile(r'^machine[\W]+%s' % re.escape(machine), flags=re.I)

    for line in lines:
        if macine_re.match(line):
            in_machine_context = True
        elif in_machine_context:
            if not line.startswith(' '):
                in_machine_context = False

        if not in_machine_context:
            modified.append(line)

    return '\n'.join(modified).rstrip()


def update_netrc_file(**kwargs):
    logger.info("Update netrc file %s", netrc_filename)
    HOST = urlparse(config['url']).netloc.split(':', 1)[0]
    macine_re = re.compile(r'^machine[\W]+%s' % re.escape(HOST), flags=re.M | re.I)

    if os.path.isfile(netrc_filename):
        with open(netrc_filename) as fd:
            netrc_content = fd.read()
    else:
        netrc_content = ''

    ctx = dict(
        email=kwargs.get('email'),
        token=kwargs.get('token'),
        host=HOST,
    )
    if macine_re.search(netrc_content):
        logger.info("Remove machine %s", HOST)
        netrc_content = remove_machine(HOST, netrc_content)
    else:
        logger.info("Machine %s does not exist in netrc", HOST)

    if kwargs.get('email') or kwargs.get('token'):
        logger.info("Adding machine %s to netrc", HOST)
        netrc_content += netrc_template % ctx
    else:
        netrc_content += '\n'

    with open(netrc_filename, 'w') as fd:
        fd.write(netrc_content)


def update_config_file(kwargs):
    logger.info("Update config file %s", config_filename)

    parser = ConfigParser()
    if os.path.isfile(config_filename):
        with open(config_filename) as fd:
            parser.read_file(fd, config_filename)

    if CONFIG_SECTION not in parser.sections():
        parser.add_section(CONFIG_SECTION)

    for key, value in kwargs.items():
        parser.set(CONFIG_SECTION, key, value)

    with open(config_filename, 'w') as fd:
        parser.write(fd)


def remove_default_values(kwargs):
    'Remove any default values'
    for key, value in default_config.items():
        if kwargs.get(key) == value:
            kwargs.pop(key)


def update_config(**kwargs):
    'Update the config in memory and files'

    config.update(kwargs)
    update_config_file(kwargs)


def update_token(email, token):
    'Update the config in memory and files'
    config.update(email=email, token=token)
    update_netrc_file(email=email, token=token)


def zipsafe_read(filename):
    'Read a file from a within a zip file location'
    # Regular file
    if os.path.exists(filename):
        with open(filename, 'rb') as fp:
            return fp.read()

    zipfile = os.path.dirname(filename)
    zipmember = os.path.basename(filename)
    while zipfile:
        if os.path.isfile(zipfile):
            with ZipFile(zipfile) as zf:
                return zf.read(zipmember)
        zipmember = os.path.join(os.path.basename(zipfile), zipmember)
        zipfile = os.path.dirname(zipfile)

    raise Exception('Could not read file {}'.format(filename))


def unpack_cache_files():
    certfile = os.path.join(cache_dirname, 'cacert.pem')

    if not os.path.isfile(certfile):
        cert = zipsafe_read(certifi.where())
        with open(certfile, 'wb') as fd:
            fd.write(cert)


def read_config():
    """
    read all configuration settings into module level singleton
    """
    config.clear()
    config.update(default_config.copy())
    load_config()
    load_netrc()
    update_config_with_env()
    unpack_cache_files()


def get_using():
    '''
    Detect if 'use' has been called and return the record
    '''

    using_file = os.path.join(cache_dirname, 'using.json')

    if not os.path.exists(using_file):
        return None

    with open(using_file) as fd:
        return json.load(fd)


def set_using(records):
    using_file = os.path.join(cache_dirname, 'using.json')

    with open(using_file, 'w') as fd:
        json.dump(records, fd, indent=2)


def unset_using():

    using_file = os.path.join(cache_dirname, 'using.json')

    if os.path.exists(using_file):
        os.unlink(using_file)

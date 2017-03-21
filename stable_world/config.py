import os
import re
import logging
import certifi
from zipfile import ZipFile
from .env import env
from .py_helpers import ConfigParser, urlparse

from netrc import netrc

logger = logging.getLogger(__name__)


def abs_expand(path): return os.path.abspath(os.path.expanduser(path))


# TODO windows locations
CONFIG_SECTION = 'stable.world'

config_filename = abs_expand(env.STABLE_WORLD_CONFIG)
netrc_filename = abs_expand(os.path.join('~', '.netrc'))
cache_dirname = abs_expand(env.STABLE_WORLD_CACHE_DIR)
certfile_default = os.path.join(cache_dirname, 'cacert.pem')

default_config = {
    'url': env.STABLE_WORLD_URL
}

config = default_config.copy()


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
        verify_https = certfile_default

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


def update_config_file():
    logger.info("Update config file %s", config_filename)
    to_write = config.copy()
    to_write.pop('email', None)
    to_write.pop('token', None)

    parser = ConfigParser()
    parser.add_section(CONFIG_SECTION)

    for key, value in to_write.items():
        parser.set(CONFIG_SECTION, key, value)

    config_dir = os.path.dirname(config_filename)
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)

    with open(config_filename, 'w') as fd:
        parser.write(fd)


def remove_default_values(kwargs):
    'Remove any default values'
    for key, value in default_config.items():
        if kwargs.get(key) == value:
            kwargs.pop(key)


def update_config(**kwargs):
    'Update the config in memory and files'

    if kwargs:
        config.update(kwargs)

    if 'email' in kwargs or 'token' in kwargs:
        update_netrc_file(**kwargs)

    kwargs.pop('email', None)
    kwargs.pop('token', None)

    remove_default_values(kwargs)

    if kwargs:
        update_config_file()


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
    if not os.path.isdir(cache_dirname):
        os.makedirs(cache_dirname)
    if not os.path.isfile(certfile_default):
        cert = zipsafe_read(certifi.where())
        with open(certfile_default, 'wb') as fd:
            fd.write(cert)
        print('certfile', certfile_default)


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

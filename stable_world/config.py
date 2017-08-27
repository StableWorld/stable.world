import os
import re
import logging
import certifi
from netrc import netrc
from zipfile import ZipFile
from .py_helpers import ConfigParser, urlparse
from . import errors

logger = logging.getLogger(__name__)

# TODO windows locations
CONFIG_SECTION = 'stable.world'


def load_config(config_filename, config):
    if os.path.isfile(config_filename):
        logger.info("load config from %s" % (config_filename))
        parser = ConfigParser()
        with open(config_filename) as fd:
            parser.read_file(fd, config_filename)
            _config = parser._sections.get(CONFIG_SECTION, {})
            config.update(_config)

    else:
        logger.info("no config file %s" % (config_filename))


def update_config(config_filename, key, value):
    parser = ConfigParser()
    if os.path.isfile(config_filename):
        logger.info("load config from %s" % (config_filename))
        with open(config_filename) as fd:
            parser.read_file(fd, config_filename)
            # _config = parser._sections.get(CONFIG_SECTION, {})
    else:
        logger.info("no config file %s" % (config_filename))

    if not parser.has_section(CONFIG_SECTION):
        parser.add_section(CONFIG_SECTION)

    parser.set(CONFIG_SECTION, key, value)
    with open(config_filename, 'w') as fd:
        parser.write(fd)


def make_directories(cache_dirname, config_filename):
    try:
        if not os.path.isdir(cache_dirname):
            os.makedirs(cache_dirname)
    except OSError:
        msg = "Could not create cache directory {}".format(cache_dirname)
        raise errors.UserError(msg)

    logdir = os.path.join(cache_dirname, 'logs')
    try:
        if not os.path.isdir(os.path.dirname(logdir)):
            os.makedirs(os.path.dirname(logdir))
    except OSError:
        # Don't want any errors here
        msg = "Do no have write perms to write logs to '{}'".format(logdir)
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


def abs_expand(path):
    return os.path.abspath(os.path.expanduser(path))


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


def unpack_cache_files(cache_dirname):
    certfile = os.path.join(cache_dirname, 'cacert.pem')
    if not os.path.isfile(certfile):
        cert = zipsafe_read(certifi.where())
        with open(certfile, 'wb') as fd:
            fd.write(cert)


def load_netrc(netrc_filename, config):

    HOST = urlparse(config['STABLE_WORLD_URL']).netloc.split(':', 1)[0]
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


def update_netrc_file(netrc_filename, url, **kwargs):
    logger.info("Update netrc file %s", netrc_filename)
    HOST = urlparse(url).netloc.split(':', 1)[0]
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

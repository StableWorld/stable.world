import os
import re
import logging
import platform
from configparser import ConfigParser

if platform.python_version_tuple()[0] == '3':
    from urllib.parse import urlparse
else:  # PY2
    from urlparse import urlparse

from netrc import netrc

logger = logging.getLogger(__name__)

# TODO windows locations
config_filename = os.path.expanduser(os.path.join('~', '.stable.world'))
netrc_filename = os.path.expanduser(os.path.join('~', '.netrc'))

default_config = {
    'url': os.getenv('STABLE_WORLD_URL', 'http://probably.stable.world')
}

config = default_config.copy()


def load_config():
    if os.path.isfile(config_filename):
        parser = ConfigParser()
        with open(config_filename) as fd:
            parser.read_file(fd, config_filename)
            _config = parser._sections['default']
            config.update(_config)
    else:
        config.update(default_config)


def load_netrc():

    HOST = urlparse(config['url']).netloc.split(':', 1)[0]
    if os.path.isfile(netrc_filename):
        EMAIL, _, TOKEN = netrc(netrc_filename).authenticators(HOST) or (None, None, None)
        config.update({'email': EMAIL, 'token': TOKEN})


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
    for key, value in to_write.items():
        parser.set('default', key, value)

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

def read_config():
    """
    read all configuration settings into module level singleton
    """
    load_config()
    load_netrc()

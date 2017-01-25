import os
import yaml
import re
from urllib.parse import urlparse
from netrc import netrc

# TODO windows locations
config_filename = os.path.expanduser(os.path.join('~', '.stable.world'))
netrc_filename = os.path.expanduser(os.path.join('~', '.netrc'))

default_config = {
    'url': os.getenv('STABLE_WORLD_URL', 'http://localhost:5000')
}

config = default_config.copy()


def load_config():
    if os.path.isfile(config_filename):
        with open(config_filename) as fd:
            _config = yaml.safe_load(fd) or {}
            config.update(_config)
    else:
        config.update(default_config)


def load_netrc():

    HOST = urlparse(config['url']).netloc.split(':', 1)[0]
    EMAIL, _, TOKEN = netrc().authenticators(HOST) or (None, None, None)
    config.update({'email': EMAIL, 'token': TOKEN})


netrc_template = '''
machine %(host)s
    login %(email)s
    password %(token)s
'''


def remove_machine(machine, netrc_content):
    lines = netrc_content.split('\n')
    modified = []

    in_machine_context = False
    for line in lines:
        if line.startswith('machine %s' % machine):
            in_machine_context = True
        elif in_machine_context:
            if not line.startswith(' '):
                in_machine_context = False

        if not in_machine_context:
            modified.append(line)

    return '\n'.join(modified)


def update_netrc_file(**kwargs):

    HOST = urlparse(config['url']).netloc.split(':', 1)[0]
    macine_re = re.compile('^machine %s' % re.escape(HOST))

    with open(netrc_filename) as fd:
        netrc_content = fd.read()

    ctx = dict(
        email=kwargs.get('email'),
        token=kwargs.get('token'),
        host=HOST,
    )

    if macine_re.match(netrc_content):

        netrc_content = remove_machine(HOST, netrc_content)

    if kwargs.get('email') or kwargs.get('token'):
        netrc_content += netrc_template % ctx

    with open(netrc_filename, 'w') as fd:
        fd.write(netrc_content)


def update_config_file():

    to_write = config.copy()
    to_write.pop('email', None)
    to_write.pop('token', None)

    with open(config_filename, 'w') as fd:
        yaml.safe_dump(to_write, fd)


def update_config(**kwargs):
    'Update the config in mem and file'

    if kwargs:
        config.update(kwargs)

    if 'email' in kwargs or 'token' in kwargs:
        update_netrc_file(**kwargs)

    kwargs.pop('email', None)
    kwargs.pop('token', None)

    if kwargs:
        update_config_file()


load_config()
load_netrc()

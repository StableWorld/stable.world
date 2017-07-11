from __future__ import print_function, unicode_literals, absolute_import
import os
import sys
import click
from base64 import b64encode
from .base import BaseManager


def read_npm_config(fd):
    results = {}
    for line in fd.readlines():
        if '=' in line:
            key, value = line.split('=', 1)
            results[key] = value
    return results


def write_npm_config(fd, url, token, extra=None):

    npm_config = dict(extra or {})

    npm_config['always-auth'] = 'true'
    npm_config['registry'] = url

    # Seems to be depricated ???
    npm_config['_auth'] = b64encode('token:{}'.format(token).encode()).decode()

    # TODO: figure out when this was implemented
    scoped_auth = '//{}:_authToken={}'.format(url.split('//', 1)[-1], token)
    print(scoped_auth, file=fd)
    for key, value in npm_config.items():
        print(key, value, sep='=', file=fd)
    return


class NPMManager(BaseManager):
    NAME = 'npm'
    PROGRAM = 'npm'

    @property
    def config_file(self):
        return os.path.expanduser('~/.npmrc')

    def use(self):
        sw_url = self.get_base_url()

        if os.path.exists(self.config_file):
            with open(self.config_file) as fd:
                existing_config = read_npm_config(fd)
        else:
            existing_config = {}

        if self.dryrun:
            click.echo('  Dryrun: Would have written config file'.format(self.config_file))
            click.echo('  ---')
            write_npm_config(sys.stdout, sw_url, self.token, existing_config)
            click.echo('  ---')
        else:
            click.echo('  Writing {} config file "{}"'.format(self.NAME, self.config_file))

            if not os.path.exists(os.path.dirname(self.config_file)):
                os.makedirs(os.path.dirname(self.config_file))

            with open(self.config_file, 'w') as fd:
                write_npm_config(fd, sw_url, self.token, existing_config)
        return {'config_files': [self.config_file]}

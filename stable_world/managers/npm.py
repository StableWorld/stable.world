from __future__ import print_function, unicode_literals, absolute_import
import os
import sys
import click
from .base import BaseManager


def read_npm_config(fd):
    results = {}
    for line in fd.readlines():
        if '=' in line:
            key, value = line.split('=', 1)
            results[key] = value
    return results


def write_npm_config(fd, obj):
    for key, value in obj.items():
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
                npm_config = read_npm_config(fd)
        else:
            npm_config = {}

        npm_config['always-auth'] = 'true'
        npm_config['registry'] = sw_url
        # TODO: implement me
        npm_config['_auth'] = 'basic'

        if self.dryrun:
            click.echo('  Dryrun: Would have written config file'.format(self.config_file))
            click.echo('  ---')
            write_npm_config(sys.stdout, npm_config)
            click.echo('  ---')
        else:
            click.echo('  Writing {} config file "{}"'.format(self.NAME, self.config_file))

            if not os.path.exists(os.path.dirname(self.config_file)):
                os.makedirs(os.path.dirname(self.config_file))

            with open(self.config_file, 'w') as fd:
                write_npm_config(fd, npm_config)

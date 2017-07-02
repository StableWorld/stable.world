from __future__ import unicode_literals

import os
import sys
import click
from pipes import quote
from .base import BaseManager
from stable_world.py_helpers import ConfigParser, platform_uname
from stable_world import errors


class PyPIManager(BaseManager):

    NAME = 'pypi'
    PROGRAM = 'pip'

    @property
    def config_file(self):
        uname = platform_uname()
        if uname.system == 'Linux':
            return os.path.expanduser('~/.config/pip/pip.conf')
        elif uname.system == 'Darwin':
            return os.path.expanduser('~/Library/Application Support/pip/pip.conf')
        elif uname.system == 'Windows':
            return '%s\pip\pip.ini' % os.getenv('APPDATA')
        else:
            raise errors.UserError('Unsupported platform %s' % uname.system)

    def use(self):

        sw_url = self.get_base_url(basicAuthRequired=True)

        parser = ConfigParser()

        if os.path.isfile(self.config_file):
            with open(self.config_file) as fd:
                parser.read(fd)

        section = 'global'
        if section not in parser.sections():
            parser.add_section(section)

        cache_url = self.cache_info['url']
        pypi_index = self.cache_info['config']['global']['index-url']

        pypi_index = pypi_index.replace(cache_url, sw_url)
        parser.set(section, 'index-url', pypi_index)
        parser.set(section, 'cache-dir', self.cache_dir)

        if self.dryrun:
            click.echo('  %-30s %s' % ('Dryrun: Would have written config file', quote(self.config_file)))
            click.echo('---')
            parser.write(sys.stdout)
            click.echo('---')
        else:
            click.echo('  %-30s %s' % ('Writing pip config file', quote(self.config_file)))

            if not os.path.exists(os.path.dirname(self.config_file)):
                os.makedirs(os.path.dirname(self.config_file))

            with open(self.config_file, 'w') as fd:
                parser.write(fd)

        return {'config_files': [self.config_file]}

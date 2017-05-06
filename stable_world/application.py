import os
from functools import wraps
import click
from stable_world import config2
from stable_world.env import env
from stable_world.client import Client

__all__ = ('StableWorldApplication', 'pass_app')


class StableWorldApplication:
    '''
    Application to store global variables
    '''

    def __init__(self):
        self.config_filename = config2.abs_expand(env.STABLE_WORLD_CONFIG)
        self.netrc_filename = config2.abs_expand(os.path.join('~', '.netrc'))
        self.cache_dirname = config2.abs_expand(env.STABLE_WORLD_CACHE_DIR)

        self.config = {
            'url': env.STABLE_WORLD_URL
        }
        self.client = Client(
            self.config.get('url'),
            self.config.get('verify_https', True)
        )

        self.cli_options = {}

    @property
    def token(self):
        return self.config.get('token')

    @property
    def email(self):
        return self.config.get('email')

    @property
    def password(self):
        return self.config.get('password')

    def make_directories(self):
        config2.make_directories(self.cache_dirname, self.config_filename)

    def read_config(self):
        config2.load_config(self.config_filename, self.config)
        config2.load_netrc(self.netrc_filename, self.config)
        config2.unpack_cache_files(self.cache_dirname)
        self.config.update(self.cli_options)

        self.client = Client(
            self.config.get('url'),
            self.config.get('verify_https', True)
        )

    def update_netrc(self, email, token):
        self.config.update(email=email, token=token)
        config2.update_netrc_file(
            self.netrc_filename, self.config['url'],
            email=email, token=token
        )

    def update_option(self, param, value):
        self.cli_options[param] = value


def pass_app(f):
    @wraps(f)
    def new_func(*args, **kwargs):
        ctx = click.get_current_context()
        app = ctx.ensure_object(StableWorldApplication)
        if app is None:
            raise RuntimeError('Managed to invoke callback without a '
                               'context object of type %r existing'
                               % StableWorldApplication.__name__)
        return ctx.invoke(f, app, *args[1:], **kwargs)
    return new_func


def set_config_option(ctx, param, value):
    if value is not None:
        app = ctx.ensure_object(StableWorldApplication)
        app.update_option(param, value)


# Options
email_option = click.option(
    '--email', default=env.STABLE_WORLD_EMAIL,
    expose_value=False,
    callback=set_config_option,
    help='Your email address'
)
password_option = click.option(
    '--password', default=env.STABLE_WORLD_PASSWORD,
    expose_value=False,
    callback=set_config_option,
    help='Your password'
)

token_option = click.option(
    '--token', default=env.STABLE_WORLD_TOKEN,
    expose_value=False,
    callback=set_config_option,
    help='An authentication token'
)

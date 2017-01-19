import os
import yaml


# TODO windows location
config_filename = os.path.expanduser(os.path.join('~', '.stable.world'))

default_config = {
    'url': os.getenv('STABLE_WORLD_URL', 'http://localhost:5000')
}

config = default_config.copy()

if os.path.isfile(config_filename):
    with open(config_filename) as fd:
        _config = yaml.safe_load(fd) or {}
        config.update(_config)
else:
    config = default_config.copy()


def update_config(**kwargs):
    'Update the config in mem and file'
    config.update(kwargs)
    with open(config_filename, 'w') as fd:
        yaml.safe_dump(config, fd)

import os
from yaml import safe_load, safe_dump

# TODO windows location
config_filename = os.path.expanduser(os.path.join('~', '.stable.world'))

config = {
    'url': os.getenv('STABLE_WORLD_URL', 'http://localhost:5000')
}

if os.path.isfile(config_filename):
    with open(config_filename) as fd:
        config = safe_load(fd)


def update_config(**kwargs):
    'Update the config in mem and file'
    config.update(kwargs)
    with open(config_filename, 'w') as fd:
        safe_dump(config, fd)

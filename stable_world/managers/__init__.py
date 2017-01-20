
from .pypi import setup_pypi
from .conda import setup_conda
from .. import errors


def setup(name, chache_info, pinned_to):
    ty = chache_info['type']
    if ty == 'pypi':
        return setup_pypi(name, chache_info, pinned_to)
    if ty == 'conda':
        return setup_conda(name, chache_info, pinned_to)

    raise errors.UserError("Don't know what to do for type %s (%s => %s)" % (ty, name, chache_info['url']))

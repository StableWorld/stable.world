
from .pypi import setup_pypi
from .conda import setup_conda
from .. import errors


def setup(ty, project, create_tag, cache_list, pinned_to):
    if ty == 'pypi':
        return setup_pypi(project, create_tag, cache_list, pinned_to)
    if ty == 'conda':
        return setup_conda(project, create_tag, cache_list, pinned_to)

    raise errors.UserError("Don't know what to do for type %s" % ty)

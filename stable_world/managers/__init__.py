import click

from .pypi import PyPIManager
from .npm import NPMManager


def use(ty, project, create_tag, cache_list, pinned_to, dryrun):

    if ty == PyPIManager.NAME:
        Manager = PyPIManager
    if ty == NPMManager.NAME:
        Manager = NPMManager
    else:
        click.echo("Don't know what to do for type %s" % ty)
        return None

    manager = Manager(project, create_tag, cache_list, pinned_to, dryrun)
    return manager.use()


def unuse(ty, info):
    if ty == PyPIManager.NAME:
        Manager = PyPIManager
    if ty == NPMManager.NAME:
        Manager = NPMManager
    else:
        click.echo("Don't know what to do for type %s" % ty)
        return None

    Manager.unuse(info)

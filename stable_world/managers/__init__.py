import click

from . import pypi
from . import conda


def use(ty, project, create_tag, cache_list, pinned_to, dryrun):
    if ty == 'pypi':
        return pypi.use(project, create_tag, cache_list, pinned_to, dryrun)
    if ty == 'conda':
        return conda.use(project, create_tag, cache_list, pinned_to, dryrun)
    else:
        click.echo("Don't know what to do for type %s" % ty)
        return None


def unuse(ty, info):
    if ty == 'pypi':
        return pypi.unuse(info)
    if ty == 'conda':
        return conda.unuse(info)

    click.echo("Don't know what to do for type %s" % ty)

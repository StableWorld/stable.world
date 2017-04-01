from __future__ import print_function
import sys

import click
from itertools import groupby

from .config import set_using, get_using, unset_using
from . import utils, errors
from . import managers


def use_project(client, create_tag, project, dryrun):
    info = client.project(project)
    already_using = get_using()

    if already_using:
        utils.echo_error()
        click.echo('You are already using tag "{tag}" from project "{project}"'.format(**already_using))
        click.echo('  To unuse this environment, please run the command:')
        click.echo('')
        click.echo('        stable.world unuse')
        click.echo('')
        sys.exit(1)

    pinned_to = info['project']['pinned_to']

    if pinned_to:
        click.secho('  Alert: ', fg='magenta', nl=False, bold=True)
        click.echo('  Project %s is ' % project, nl=False)
        click.secho('pinned', nl=False, bold=True)
        click.echo(' to tag %s' % pinned_to['name'])

        click.echo('  The current environment will be set up to replay %s' % pinned_to['name'])
        click.echo('  Tag "%s" will not be used' % create_tag)
        click.echo('')
    else:
        try:
            if not dryrun:
                client.add_tag(project, create_tag)
            else:
                utils.echo_warning()
                click.echo('Dryrun: not creating tag')
        except errors.DuplicateKeyError:
            utils.echo_warning()
            click.echo('The tag already exists. You may want to create a new tag')
            utils.echo_warning()
            click.echo('You are going to record over any previous changes')
            click.echo('')

        click.echo("  Tag %s added to project %s" % (create_tag, project))
        click.echo('')

    urls = info['project']['urls']

    groups = groupby(urls.items(), lambda item: item[1]['type'])
    tag = pinned_to['name'] if pinned_to else create_tag
    using_record = {'types': {}, 'tag': tag, 'project': project}
    for ty, cache_group in groups:
        # import pdb; pdb.set_trace()
        cache_list = list(cache_group)
        details = managers.use(ty, project, create_tag, cache_list, pinned_to, dryrun)
        using_record['types'][ty] = details
    click.echo('')

    if not dryrun:
        set_using(using_record)

        utils.echo_success()
        what = 'replaying from' if pinned_to else 'recording into'
        click.echo('You are %s tag "%s" in project "%s"' % (what, tag, project))
        click.echo('')
    else:
        utils.echo_success()
        click.echo('Dryrun Completed')
        click.echo('')


def unuse_project():
    using = get_using()
    if not using:
        utils.echo_error()
        click.echo('You are not currently using a project')
        sys.exit(1)

    for ty, info in using['types'].items():
        managers.unuse(ty, info)

    click.echo('')

    unset_using()

    utils.echo_success()
    click.echo("No longer using project %s" % (using['project']))

    return

from __future__ import print_function
import sys

import click
from itertools import groupby

from stable_world.config import set_using, get_using, unset_using
from stable_world import utils, errors
from stable_world import managers


def setup_tags(client, project, create_tag, info, dryrun):
    pinned_to = info['project']['pinned_to']

    if pinned_to and create_tag:
        click.secho('  Alert: ', fg='magenta', nl=False, bold=True)
        click.echo('  Project %s is ' % project, nl=False)
        click.secho('pinned', nl=False, bold=True)
        click.echo(' to tag %s' % pinned_to['name'])
        click.echo('  Tag "%s" will not be used' % create_tag)
        click.echo('')
    else:
        if create_tag and not dryrun:
            try:
                client.add_tag(project, create_tag)
            except errors.DuplicateKeyError:
                utils.echo_warning()
                click.echo('The tag already exists. You may want to create a new tag')
                utils.echo_warning()
                click.echo('You are going to record over any previous changes')
                click.echo('')
        elif create_tag and dryrun:
            utils.echo_warning()
            click.echo('Dryrun: not creating tag')

        click.echo("  Tag %s added to project %s" % (create_tag, project))
        click.echo('')


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

    setup_tags(client, project, create_tag, info, dryrun)

    urls = info['project']['urls']

    groups = groupby(urls.items(), lambda item: item[1]['type'])
    using_record = {'types': {}, 'project': project}
    for ty, cache_group in groups:
        # import pdb; pdb.set_trace()
        cache_list = list(cache_group)
        details = managers.use(ty, project, cache_list, dryrun)
        using_record['types'][ty] = details
    click.echo('')

    if not dryrun:
        set_using(using_record)

        utils.echo_success()
        click.echo('You are using project "{}"'.format(project))
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
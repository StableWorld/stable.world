from __future__ import print_function
import sys

import click
from itertools import groupby

# from stable_world.simple_token import test_token
from stable_world import utils, errors
from stable_world import managers


def setup_tags(client, bucket, create_tag, info, dryrun):
    pinned_to = info['bucket']['pinned_to']

    if pinned_to and create_tag:
        click.secho('  Alert: ', fg='magenta', nl=False, bold=True)
        click.echo('  bucket %s is ' % bucket, nl=False)
        click.secho('pinned', nl=False, bold=True)
        click.echo(' to tag %s' % pinned_to['name'])
        click.echo('  Tag "%s" will not be used' % create_tag)
        click.echo('')
    else:
        if create_tag and not dryrun:
            try:
                client.add_tag(bucket, create_tag)
            except errors.DuplicateKeyError:
                utils.echo_warning()
                click.echo('The tag already exists. You may want to create a new tag')
                utils.echo_warning()
                click.echo('You are going to record over any previous changes')
                click.echo('')
        elif create_tag:
            if dryrun:
                utils.echo_warning()
                click.echo('Dryrun: not creating tag')
            else:
                click.echo("  Tag %s added to bucket %s" % (create_tag, bucket))
                click.echo('')


def use_bucket(app, create_tag, bucket, token, dryrun):

    app.client.check_bucket_token(bucket, token)

    already_using = app.get_using()

    if already_using:
        utils.echo_error()
        click.echo('You are already using bucket "{bucket}"'.format(**already_using))
        click.echo('  To unuse this environment, please run the command:')
        click.echo('')
        click.echo('        stable.world unuse')
        click.echo('')
        sys.exit(1)

    info = app.client.bucket(bucket)
    setup_tags(app.client, bucket, create_tag, info, dryrun)

    urls = info['bucket']['urls']

    grouper = groupby(urls.items(), lambda item: item[1]['type'])
    groups = sorted((key, list(group)) for key, group in grouper)

    using_record = {'types': {}, 'bucket': bucket}
    for ty, cache_group in groups:
        cache_list = list(cache_group)
        details = managers.use(app.client.site, ty, bucket, cache_list, token, dryrun)
        using_record['types'][ty] = details
    click.echo('')

    if not dryrun:
        app.set_using(using_record)

        utils.echo_success()
        click.echo('You are using bucket "{}"'.format(bucket))
        click.echo('')
    else:
        utils.echo_success()
        click.echo('Dryrun Completed')
        click.echo('')


def unuse_bucket(app):
    using = app.get_using()
    if not using:
        utils.echo_error()
        click.echo('You are not currently using a bucket')
        sys.exit(1)

    for ty, info in using['types'].items():
        managers.unuse(ty, info)

    click.echo('')

    app.unset_using()

    utils.echo_success()
    click.echo("No longer using bucket %s" % (using['bucket']))

    return

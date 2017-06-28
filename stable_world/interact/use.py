from __future__ import print_function
import sys

import click
from itertools import groupby

from stable_world import utils
from stable_world import managers


def use_bucket(app, bucket, token, dryrun):

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

    if info['bucket']['frozen']:
        click.secho('  Alert: ', fg='magenta', nl=False, bold=True)
        click.echo('  bucket %s is ' % bucket, nl=False)
        click.secho('frozen', nl=False, bold=True)
        click.echo('.  New objects will not be added to bucket')
        click.echo('')

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

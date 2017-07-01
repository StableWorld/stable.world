from __future__ import print_function
import sys

import click
from stable_world import utils


def check_bucket(app, bucket_name, token):
    """
    Test that a bucket is available
    If frozen, it will print a warning
    test that the token has the correct scopes
    """
    app.client.check_bucket_token(bucket_name, token)

    info = app.client.bucket(bucket_name)

    if info['bucket']['frozen']:
        click.secho('  Alert: ', fg='magenta', nl=False, bold=True)
        click.echo('  bucket %s is ' % bucket_name, nl=False)
        click.secho('frozen', nl=False, bold=True)
        click.echo('.  New objects will not be added to bucket')
        click.echo('')

    return info['bucket']['urls']

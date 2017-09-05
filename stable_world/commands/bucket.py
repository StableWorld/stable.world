import click
from stable_world import utils, output


@click.group()
def main():
    pass


@main.command('bucket:create')
@click.argument('name')
@utils.login_required
def bucket_create(app, name):
    "Create a new bucket"
    info = app.client.add_bucket(name)
    output.buckets.print_bucket(info['bucket'])
    utils.echo_success()
    click.echo('Bucket "%s" added!' % info['bucket']['name'])


@main.command('bucket:list')
@utils.login_required
def bucket_list(app):
    "list all buckets you have access to"
    buckets = app.client.buckets()
    output.buckets.print_buckets(buckets)


@main.command('bucket')
@utils.bucket_name_argument()
@utils.login_required
def bucket(app, name):
    "show a published bucket"
    info = app.client.bucket(name)
    output.buckets.print_bucket(info['bucket'])


@main.command('bucket:destroy')
@utils.bucket_name_argument()
@utils.login_required
def bucket_destroy(app, name):
    "tear down a published bucket"
    app.client.delete_bucket(name)
    utils.echo_success()
    click.echo(' Bucket %s removed' % bucket)


@main.command('bucket:cache:add')
@utils.bucket_name_argument()
@click.option('--url', help='The url endpoint to cache')
@click.option('--type', help='type of cache')
@click.option('-n', '--cache-name', required=True, help='Give it a name')
@utils.login_required
def bucket_cache_add(app, name, url, type, cache_name):
    "Add a cache to the bucket"

    app.client.add_url(name, url, cache_name, type)

    utils.echo_success()
    click.echo(' Cache %s was added as %s' % (url, cache_name))


@main.command('bucket:cache:remove')
@utils.bucket_name_argument()
@click.option('-n', '--cache-name', help='name of cache to remove')
@utils.login_required
def bucket_cache_remove(app, name, cache_name):
    "Remove a cache from the bucket"

    info = app.client.remove_url(name, cache_name)
    utils.echo_success()
    click.echo(' Cache %s (%s) was removed' % (info['url'], cache_name))


@main.command('bucket:objects')
@click.option(
    '-w', '--since', default=None,
    type=utils.datetime_type,
    help='Show objects after date',
)
@utils.bucket_name_argument()
@utils.login_optional
def bucket_objects(app, name, since=None):
    """Show the objects added to a bucket since a time"""

    if since:
        objects = app.client.objects_since(name, since)
    else:
        objects = app.client.objects(name)

    output.buckets.print_objects(objects)


@main.command('bucket:rollback')
@click.option(
    '-w', '--when', required=True, default=None,
    type=utils.datetime_type,
    help='Rollback after',
)
@utils.bucket_name_argument()
@utils.login_optional
def bucket_rollback(app, name, when):
    """Show the objects added to a bucket since a time"""

    app.client.rollback(name, when)

    utils.echo_success()
    click.echo("Bucket %s rolled back to %s" % (name, when.ctime()))


@main.command('bucket:freeze')
@utils.bucket_name_argument()
@utils.login_required
def bucket_freeze(app, name):
    "Freeze a bucket so it can not be modified"
    app.client.freeze(name)
    utils.echo_success()
    click.echo("Bucket %s frozen" % (name))


@main.command('bucket:unfreeze')
@utils.bucket_name_argument()
@utils.login_required
def bucket_unfreeze(app, name):
    "Unfreeze a bucket so it can be modified"
    app.client.unfreeze(name)
    utils.echo_success()
    click.echo("Unfroze Bucket %s" % (name))

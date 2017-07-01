import click


def print_buckets(buckets):
    click.echo('  buckets')
    for bucket in buckets:

        frozen = '[frozen]' if bucket['frozen'] else ''

        click.echo('    + %-25s' % (bucket['name'] + frozen), nl=False)
        if bucket['urls']:
            urls = '(%s)' % ', '.join(bucket['urls'].keys())
        else:
            urls = 'empty'
        click.echo(urls)


def print_bucket(bucket):
    frozen = '[frozen]' if bucket['frozen'] else ''

    click.echo('  bucket: %-25s' % (bucket['name'] + frozen))

    click.echo('  Caches:')
    for name, info in bucket['urls'].items():
        click.echo('    %10s => %s' % (name, info['url']))


def print_objects(info):

    objects = info.get('objects')

    if not objects:
        click.echo('  No sources in this bucket')
        return

    for obj in objects:
        click.echo('   - {}'.format(obj['source']))

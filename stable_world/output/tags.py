from dateutil.parser import parse as parse_date
import click


def print_tags(tag_list):
    print('    Tags:')
    for tag in tag_list:
        date = parse_date(tag['created'])
        click.echo('      - %-10s' % tag['name'], nl=False)
        click.secho(date.ctime(), dim=True)


def print_diff_items(items):
    sources = sorted(item['source'] for item in items)
    for source in sorted(sources):
        print('    + ', source)


def diff_tags(diff_result):

    tag_info = diff_result['tags']['first'], diff_result['tags']['last']
    print_tags(tag_info)

    if len(diff_result['diff']['added']):
        print('Added:')
    print_diff_items(diff_result['diff']['added'])

    if len(diff_result['diff']['removed']):
        print('Removed:')
    print_diff_items(diff_result['diff']['removed'])

    if len(diff_result['diff']['modified']):
        print('Modified:')
    print_diff_items(diff_result['diff']['modified'])


def print_objects(info):

    objects = info.get('objects')

    if not objects:
        click.echo('  No sources in this tag')
        return

    for source in objects:
        click.echo('   - {}'.format(source))

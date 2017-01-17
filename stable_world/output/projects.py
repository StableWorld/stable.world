import click


def print_projects(projects):
    click.echo('  Projects')
    for project in projects:

        if project['pinned_to']:
            pinned = '[pinned:%s]' % project['pinned_to']['name']
        else:
            pinned = ''

        click.echo('    + %-25s' % (project['name'] + pinned), nl=False)
        if project['urls']:
            urls = '(%s)' % ', '.join(project['urls'].keys())
        else:
            urls = 'empty'
        click.echo(urls)

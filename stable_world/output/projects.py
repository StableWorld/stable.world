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


def print_project(project):
    if project.get('pinned_to'):
        pinned = '[pinned:%s]' % project['pinned_to']['name']
    else:
        pinned = ''

    click.echo('  Project: %-25s' % (project['name'] + pinned))

    click.echo('  Caches:')
    for name, info in project['urls'].items():
        click.echo('    %10s => %s' % (name, info['url']))

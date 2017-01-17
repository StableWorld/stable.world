import click


def print_projects(projects):
    click.echo('  Projects')
    for project in projects:
        if project['urls']:
            urls = '(%s)' % ', '.join(project['urls'].keys())
        else:
            urls = 'empty'
        click.echo('    + %-20s %s' % (project['name'], urls))

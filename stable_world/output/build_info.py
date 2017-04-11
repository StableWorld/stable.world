import click
import time
from dateutil.parser import parse as parse_date
from dateutil.tz import tzutc
from contextlib import contextmanager

from stable_world.config import config
from stable_world import errors, __version__ as version
from .utils import prettydate


@contextmanager
def echo_response_time():
    start = time.time()
    try:
        yield
    except errors.PZError as err:
        click.secho("{}: {}".format(type(err).__name__, err), fg='red')
    else:
        duration = (time.time() - start) * 1000
        click.secho("%ims response" % duration, dim=True)


def echo_info(info):

    if info is None:
        click.echo("    + No additional info available")
        click.echo("")
        return

    buildTime = parse_date(info.get('buildTime', '1900'))
    if not buildTime.tzinfo:
        buildTime = buildTime.replace(tzinfo=tzutc())

    click.echo("    + version: %s" % info.get('version', '?'))
    click.echo("    + built: %s " % prettydate(buildTime), nl=False)
    click.secho('(%s)' % buildTime.ctime(), dim=True)
    click.echo("")


def echo_api_info(client):
    click.echo("  API: ", nl=False)
    info = None
    with echo_response_time():
        info = client.api_info()

    echo_info(info)


def echo_auth_info(client):
    click.echo("  AUTH: ", nl=False)
    info = None
    with echo_response_time():
        info = client.auth_info()

    echo_info(info)


def echo_cache_info(client):
    click.echo("  CACHE: ", nl=False)
    info = None
    with echo_response_time():
        info = client.cache_info()

    echo_info(info)


def echo_html_info(client):
    click.echo("  APP: ", nl=False)
    with echo_response_time():
        info = client.html_info()

    echo_info(info)


def echo_router_info(client):
    click.echo("  ROUTER: ", nl=False)
    with echo_response_time():
        info = client.router_info()

    echo_info(info)


def build_info(client):
    'Print build information and exit'

    click.echo("")
    click.echo("  CLI Version: {}".format(version))
    click.echo("  STABLE_WORLD_URL: {}".format(config['url']))
    click.echo("")

    echo_auth_info(client)
    echo_api_info(client)
    echo_cache_info(client)
    echo_html_info(client)
    echo_router_info(client)

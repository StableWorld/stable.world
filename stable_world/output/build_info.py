import click
import time
from dateutil.parser import parse as parse_date
from dateutil.tz import tzutc
from contextlib import contextmanager

from stable_world.config import config
from .utils import prettydate


@contextmanager
def echo_response_time():
    start = time.time()
    yield
    duration = (time.time() - start) * 1000
    click.secho("%ims response" % duration, dim=True)


def echo_info(info):
    buildTime = parse_date(info.get('buildTime', '1900'))
    if not buildTime.tzinfo:
        buildTime = buildTime.replace(tzinfo=tzutc())

    click.echo("    + version: %s" % info.get('version', '?'))
    click.echo("    + built: %s " % prettydate(buildTime), nl=False)
    click.secho('(%s)' % buildTime.ctime(), dim=True)
    click.echo("")


def echo_api_info(client):
    click.echo("  API: ", nl=False)
    with echo_response_time():
        api_info = client.api_info()

    echo_info(api_info)


def echo_cache_info(client):
    click.echo("  CACHE: ", nl=False)
    with echo_response_time():
        cache_info = client.cache_info()

    echo_info(cache_info)


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
    click.echo("  STABLE_WORLD_URL: %s" % config['url'])
    click.echo("")

    echo_api_info(client)
    echo_cache_info(client)
    echo_html_info(client)
    echo_router_info(client)

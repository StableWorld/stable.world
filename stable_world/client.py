import requests
import logging
import sys
import platform
from functools import wraps

from .py_helpers import JSONDecodeError, platform_uname

from stable_world import __version__ as version

from . import errors

logger = logging.getLogger(__name__)


def request(method):
    """
    Decorate the request class with methods eg get, post
    """
    def req(self, path, payload=None, auth=None):
        url = '%s%s' % (self.site, path)
        kwargs = {}
        if auth:
            kwargs['auth'] = auth
        res = self._session.request(method, url, json=payload, **kwargs)

        logger.debug('[%s] %s - %s', method.upper(), url, res.status_code)
        self._check_response(res)
        logger.debug(res.json())
        return res.json()
    return req


def url(url_template, test_method='options'):
    """
    Try to pull the url out of each method into a decorator
    so we can perform some static analysys
    """
    def decorator(func):
        func.__dict__.setdefault('url_templates', {})
        func.url_templates[url_template] = test_method

        @wraps(func)
        def inner(self, *args, **kwargs):
            return func(self, url_template, *args, **kwargs)
        return inner
    return decorator


class Client(object):
    """
    Client for connecting with the API
    """
    def __init__(self, site, verify=True, token=None):
        self.site = site
        self._session = requests.Session()
        self._session.verify = verify

        self._session.headers['User-Agent'] = self.user_agent

        if token:
            self._session.auth = ('token', token)

    @property
    def user_agent(self):
        uname = platform_uname()
        ctx = (
            version,
            sys.version_info,
            uname
        )
        return (
            'stable.world {0}; '
            'Python {1.major}.{1.minor}.{1.micro}; '
            'OS {2.system} {2.release} {2.machine}'
        ).format(*ctx)

    get = request('get')
    post = request('post')
    delete = request('delete')

    @classmethod
    def url_templates(cls):
        url_templates = [
            method.url_templates for method in cls.__dict__.values()
            if getattr(method, 'url_templates', None)
        ]
        return {template: method for submap in url_templates for template, method in submap.items()}

    def _check_response(self, res):
        if 'sw-hint' in res.headers:
            logger.debug('Response Hint: "{}"'.format(res.headers['sw-hint']))

        try:
            payload = res.json()
        except JSONDecodeError:
            raise errors.PZError('[%s] - response was not valid json' % res.status_code)

        if 'error' in payload:
            Error = getattr(errors, payload['error'], errors.PZError)
            raise Error(payload.get('message', payload['error']), payload)

    @url('/dist/build-info.json', test_method='get')
    def html_info(self, url):
        # TODO: use url decorator when options is supported
        return self.get(url)

    @url('/router/build-info.json', test_method='get')
    def router_info(self, url):
        # TODO: use url decorator when options is supported
        return self.get(url)

    @url('/auth/')
    def auth_info(self, url):
        return self.get(url)

    @url('/api/')
    def api_info(self, url):
        return self.get(url)

    @url('/cache/', test_method='get')
    def cache_info(self, url):
        return self.get(url)

    @url('/auth/register')
    def register(self, url, email, password):

        res = self.post(
            url, dict(email=email, password=password)
        )
        return res['token']

    @url('/auth/token')
    def token(self, url, email, password, scopes=None):

        res = self.post(
            url, dict(email=email, password=password, scopes=scopes)
        )
        return res['token']

    @url('/auth/me')
    def whoami(self, url):
        res = self.get(url)
        return res['user'].get('email', 'anonymous')

    @url('/api/buckets/{bucket}')
    def add_bucket(self, url, bucket):
        res = self.post(url.format(bucket=bucket))
        return res

    @url('/api/buckets/{bucket}/url/{name}')
    def add_url(self, url, bucket, cache_url, name, type):
        to = url.format(bucket=bucket, name=name)
        self.post(to, {'url': cache_url, 'type': type})
        return

    @url('/api/buckets/{bucket}/url/{name}')
    def remove_url(self, bucket, name):
        res = self.delete(url.format(bucket=bucket, name=name))
        return res

    @url('/api/buckets/')
    def buckets(self, url):
        res = self.get(url)
        return res['buckets']

    @url('/api/buckets/{bucket}')
    def bucket(self, url, bucket):
        res = self.get(url.format(bucket=bucket))
        return res

    @url('/api/buckets/{bucket}/checkToken')
    def check_bucket_token(self, url, bucket, token):
        res = self.post(url.format(bucket=bucket), auth=('token', token))

        return res

    @url('/api/buckets/{bucket}')
    def delete_bucket(self, url, bucket):
        self.delete(url.format(bucket=bucket))
        return

    @url('/api/tags/{bucket}/{name}')
    def add_tag(self, url, bucket, name):
        self.post(
            url.format(bucket=bucket, name=name),
            dict(hostname=platform.node())
        )
        return

    @url('/api/tags/{bucket}/{first}/diff/{last}')
    @url('/api/tags/{bucket}/{first}/diff')
    def diff(self, url_one, url_two, bucket, first, last=None):
        if last:
            payload = self.get(url_one.format(bucket=bucket, first=first, last=last))
        else:
            payload = self.get(url_two.format(bucket=bucket, first=first))
        return payload

    @url('/api/buckets/{bucket}/pin/{tag}')
    def pin(self, url, bucket, tag):
        self.post(url.format(bucket=bucket, tag=tag))
        return

    @url('/api/buckets/{bucket}/pin')
    def unpin(self, url, bucket):
        self.delete(url.format(bucket=bucket))
        return

    @url('/api/tags/{bucket}/{tag}/objects')
    def tag_objects(self, url, bucket, tag, exact=False):
        to = (url + '?exact={exact}').format(
            bucket=bucket, tag=tag, exact='yes' if exact else ''
        )
        return self.get(to)

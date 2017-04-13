import requests
import logging
import sys
import platform
from functools import wraps

from .py_helpers import JSONDecodeError, platform_uname

from stable_world import __version__ as version

from .config import config
from . import errors

logger = logging.getLogger(__name__)


def request(method):
    """
    Decorate the request class with methods eg get, post
    """
    def req(self, path, payload=None):
        url = '%s%s' % (config['url'], path)
        res = self._session.request(method, url, json=payload)
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


class Client:
    """
    Client for connecting with the API
    """
    def __init__(self, token):
        self._session = requests.Session()

        uname = platform_uname()

        ctx = (
            version,
            sys.version_info,
            uname
        )
        user_agent = (
            'stable.world {0}; '
            'Python {1.major}.{1.minor}.{1.micro}; '
            'OS {2.system} {2.release} {2.machine}'
        ).format(*ctx)

        self._session.verify = config.get('verify_https')
        self._session.headers['User-Agent'] = user_agent
        self.token = token

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

    @property
    def token(self):
        raise AttributeError('token is not a readable property')

    @token.setter
    def token(self, token):
        if token:
            self._session.headers['Authorization'] = 'Bearer %s' % token
        else:
            self._session.headers.pop('Authorization', None)

        self._token = token

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
    def login(self, url, email, password):

        res = self.post(
            url, dict(email=email, password=password)
        )
        return res['token']

    @url('/auth/me')
    def whoami(self, url):
        res = self.get(url)
        return res['user'].get('email', 'anonymous')

    @url('/api/projects/{project}')
    def add_project(self, url, project):
        res = self.post(url.format(project=project))
        return res

    @url('/api/projects/{project}/url/{name}')
    def add_url(self, url, project, cache_url, name, type):
        to = url.format(project=project, name=name)
        self.post(to, {'url': cache_url, 'type': type})
        return

    @url('/api/projects/{project}/url/{name}')
    def remove_url(self, project, name):
        res = self.delete(url.format(project=project, name=name))
        return res

    @url('/api/projects/')
    def projects(self, url):
        res = self.get(url)
        return res['projects']

    @url('/api/projects/{project}')
    def project(self, url, project):
        res = self.get(url.format(project=project))
        return res

    @url('/api/projects/{project}')
    def delete_project(self, url, project):
        self.delete(url.format(project=project))
        return

    @url('/api/tags/{project}/{name}')
    def add_tag(self, url, project, name):
        self.post(
            url.format(project=project, name=name),
            dict(hostname=platform.node())
        )
        return

    @url('/api/tags/{project}/{first}/diff/{last}')
    @url('/api/tags/{project}/{first}/diff')
    def diff(self, url_one, url_two, project, first, last=None):
        if last:
            payload = self.get(url_one.format(project=project, first=first, last=last))
        else:
            payload = self.get(url_two.format(project=project, first=first))
        return payload

    @url('/api/projects/{project}/pin/{tag}')
    def pin(self, url, project, tag):
        self.post(url.format(project=project, tag=tag))
        return

    @url('/api/projects/{project}/pin')
    def unpin(self, url, project):
        self.delete(url.format(project=project))
        return

    @url('/api/tags/{project}/{tag}/objects')
    def tag_objects(self, url, project, tag, exact=False):
        to = (url + '?exact={exact}').format(
            project=project, tag=tag, exact='yes' if exact else ''
        )
        return self.get(to)

import requests
import logging
import sys
import platform

from stable_world import __version__ as version

from .config import config
from . import errors

logger = logging.getLogger(__name__)


def request(method):
    def req(self, path, payload=None):
        url = '%s%s%s' % (config['url'], '/api', path)
        res = self._session.request(method, url, json=payload)
        logger.debug('[%s] %s - %s', method.upper(), url, res.status_code)
        self._check_response(res)
        return res.json()
    return req


class Client:
    """
    Client for connecting with the API
    """
    def __init__(self, token):
        self._session = requests.Session()
        ctx = (
            version,
            sys.version_info,
            platform.uname()
        )
        user_agent = (
            'stable.world {0}; '
            'Python {1.major}.{1.minor}.{1.micro}; '
            'OS {2.system} {2.release} {2.machine}'
        ).format(*ctx)

        self._session.headers['User-Agent'] = user_agent
        self.token = token

    get = request('get')
    post = request('post')
    delete = request('delete')

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
        payload = res.json()

        if 'error' in payload:
            Error = getattr(errors, payload['error'], errors.PZError)
            raise Error(payload['message'], payload)

    def login_or_register(self, email, password):

        res = self.post(
            '/account/login_or_register',
            dict(email=email, password=password)
        )

        return res['token']

    def whoami(self):
        res = self.get('/account/user')
        return res['user'].get('email', 'anonymous')

    def add_project(self, project):
        res = self.post('/projects/%s' % project)
        return res

    def add_url(self, project, url, type, name):
        to = '/projects/%s/url/%s' % (project, name)
        self.post(to, {'url': url, 'type': type})
        return

    def remove_url(self, project, name):
        res = self.delete('/projects/%s/url/%s' % (project, name))
        return res

    def projects(self):
        res = self.get('/projects')
        return res['projects']

    def project(self, project):
        res = self.get('/projects/%s' % project)
        return res

    def delete_project(self, project):
        self.delete('/projects/%s' % project)
        return

    def tag(self, project, name):
        self.post('/tags/%s/%s' % (project, name))
        return

    def diff(self, project, first, last=None):
        if last:
            payload = self.get('/tags/%s/%s/diff/%s' % (project, first, last))
        else:
            payload = self.get('/tags/%s/%s/diff' % (project, first))

        return payload

    def pin(self, project, tag):
        self.post('/projects/%s/pin/%s' % (project, tag))
        return

    def unpin(self, project):
        self.delete('/projects/%s/pin' % project)
        return

    def tag_objects(self, project, tag):
        return self.get('/tags/%s/%s/objects' % (project, tag))

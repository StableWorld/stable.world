import requests
import logging

from .config import config
from . import errors

logger = logging.getLogger(__name__)


def request(method):
    def req(self, path, payload=None):
        url = '%s%s' % (config['url'], path)
        res = self._session.request(method, url, json=payload)
        logger.debug('[%s] %s - %s', method.upper(), url, res.status_code)
        self._check_response(res)
        return res.json()
    return req


class Client:
    """
    Client for connecting with the API
    """
    def __init__(self, email, token=None):
        self.email = email
        self._session = requests.Session()
        self.token = token

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._session.headers['Authorization'] = 'Bearer %s' % token
        self._token = token

    get = request('get')
    post = request('post')
    delete = request('delete')

    def _check_response(self, res):
        payload = res.json()

        if 'error' in payload:
            Error = getattr(errors, payload['error'], errors.PZError)
            raise Error(payload['message'], payload)

    @classmethod
    def from_login_or_register(cls, email, password):
        client = cls(email)
        token = client.login_or_register(email, password)
        client.token = token
        return client

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
        res = self.post('/spaces/%s' % project)
        return res

    def add_url(self, project, url, type, name):
        to = '/spaces/%s/url/%s' % (project, name)
        self.post(to, {'url': url, 'type': type})
        return

    def remove_url(self, project, name):
        res = self.delete('/spaces/%s/url/%s' % (project, name))
        return res

    def projects(self):
        res = self.get('/spaces')
        return res['spaces']

    def project(self, project):
        res = self.get('/spaces/%s' % project)
        return res

    def delete_project(self, project):
        self.delete('/spaces/%s' % project)
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
        self.post('/spaces/%s/pin/%s' % (project, tag))
        return

    def unpin(self, project):
        self.delete('/spaces/%s/pin' % project)
        return

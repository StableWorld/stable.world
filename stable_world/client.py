import requests

from .config import config
from . import errors


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

    def get(self, path):
        res = self._session.get('%s%s' % (config['url'], path))
        self._check_response(res)
        return res.json()

    def post(self, path, payload=None):
        res = self._session.post('%s%s' % (config['url'], path), json=payload)
        self._check_response(res)
        return res.json()

    def _check_response(self, res):
        payload = res.json()

        if 'error' in payload:
            Error = getattr(errors, payload['error'], errors.PZError)
            raise Error(payload['message'])

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

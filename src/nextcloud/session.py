# -*- coding: utf-8 -*-
from functools import wraps
import requests
from .compat import encode_requests_password

import logging
_logger = logging.getLogger(__name__)


class NextCloudConnectionError(Exception):
    """ A connection error occurred """

class NextCloudLoginError(Exception):
    """ A login error occurred """

def catch_connection_error(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.RequestException as e:
            raise NextCloudConnectionError(
                'Failed to establish connection to NextCloud', getattr(e.request, 'url', None), e)

    return wrapper


class Session(object):
    """ Session for requesting """

    def __init__(self, url=None, user=None, password=None, auth=None, session_kwargs=None):
        self.session = None
        self.auth = None
        self.user = None
        self._set_credentials(user, password, auth)
        self.url = url.rstrip('/')
        self._session_kwargs = session_kwargs or {}

    def _set_credentials(self, user, password, auth):
        if auth:
            self.auth = auth
        if user:
            self.user = user
        else:
            if isinstance(self.auth, tuple):
                self.user = self.auth[0]
            else:
                if isinstance(self.auth, requests.auth.AuthBase):
                    self.user = self.auth.username
        if not self.auth and (self.user and password):
            self.auth = (self.user, encode_requests_password(password))

    def request(self, method, url, **kwargs):
        if self.session:
            return self.session.request(method=method, url=url, **kwargs)
        else:
            _kwargs = self._session_kwargs
            _kwargs.update(kwargs)
            if not kwargs.get('auth', False):
                _kwargs['auth'] = self.auth
            return requests.request(method, url, **_kwargs)

    def login(self, user=None, password=None, auth=None, client=None):
        """Create a stable session on the server.

        :param user_id: user id
        :param password: password
        :param auth: object for any auth method
        :param client: object for any auth method
        :raises: HTTPResponseError in case an HTTP error status was returned
        """
        self.session = requests.Session()
        for k in self._session_kwargs:
            setattr(self.session, k, self._session_kwargs[k])

        self._set_credentials(user, password, auth)
        self.session.auth = self.auth
        if client:
            self._check_session(client.with_attr(json_output=True), retry=3)


    def _check_session(self, client=None, retry=None):
        def _clear():
            if self.session:
                self.logout()

        def _raise(e):
            if retry:
                _logger.warning('Retry session check (%s)', self.url)
                return self._check_session(client, retry=retry - 1)
            else:
                _clear()
                raise e

        try:
            resp = client.get_user()
            if not resp.is_ok:
                _raise(NextCloudLoginError(
                        'Failed to login to NextCloud', self.url, resp))
        except requests.exceptions.SSLError as e:
            _raise(e)
        except NextCloudConnectionError as e:
            _raise(e)
        except Exception as e:
            _clear()
            raise e

    def logout(self):
        """Log out the authenticated user and close the session.

        :returns: True if the operation succeeded, False otherwise
        :raises: HTTPResponseError in case an HTTP error status was returned
        """
        self.session.close()
        self.session = None
        return True

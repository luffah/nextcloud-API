# -*- coding: utf-8 -*-
""" Concrete part for managing sessions and requests """
import logging
import time
import requests
from .compat import encode_requests_password
from .codes import ExternalApiCodes
from .response import BaseResponse

_LOGGER = logging.getLogger(__name__)


class NextCloudConnectionError(Exception):
    """ A connection error occurred """

    def __init__(self, msg='', url='', obj=None):
        self.message = msg
        self.url = url
        self.obj = obj
        Exception.__init__(self, msg, url, obj)

class NextCloudLoginError(NextCloudConnectionError):
    """ A login error occurred """



# pylint: disable=useless-object-inheritance
class Session(object):
    """ Session for requesting """

    # pylint: disable=too-many-arguments
    def __init__(self, url=None, user=None, password=None, auth=None, session_kwargs=None):
        self.session = None
        self.auth = None
        self.user = None
        self._set_credentials(user, password, auth)
        self.url = url.rstrip('/')
        session_kwargs = session_kwargs or {}
        self._login_check = session_kwargs.pop('login_check', True)  # TODO False
        self._session_kwargs = session_kwargs

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
        """
        Use 'requests' lib to apply request with current session if logged.

        :param method (str):   the method name
        :param url (str):      the full url
        :param headers (dict): the headers
        :param params (dict):  requests parameters
        :param data:           data to push with the request

        :returns: requests.Response
        """
        try:
            print(locals())
            if self.session:
                ret = self.session.request(method=method, url=url, **kwargs)
            else:
                _kwargs = self._session_kwargs
                _kwargs.update(kwargs)
                if not kwargs.get('auth', False):
                    _kwargs['auth'] = self.auth
                ret = requests.request(method, url, **_kwargs)
                # print(ret.status_code)
                # if ret.status_code == HTTP_CODES.unauthorized:
                #     raise NextCloudConnectionError(
                #         'Not authorized', url, method)
            return ret
        except requests.RequestException as request_error:
            print(request_error)
            raise NextCloudConnectionError(
                'Failed to establish connection to NextCloud',
                getattr(request_error.request, 'url', None), request_error)

    def login(self, user=None, password=None, auth=None, client=None):
        """Create a stable session on the server.

        :param user_id: user id
        :param password: password
        :param auth: object for any auth method
        :param client: object for any auth method
        :raises: HTTPResponseError in case an HTTP error status was returned
        """
        # a = requests.adapters.HTTPAdapter(max_retries=3)

        self.session = requests.Session()

        # self.session.mount('https://', a)

        for k in self._session_kwargs:
            setattr(self.session, k, self._session_kwargs[k])

        self._set_credentials(user, password, auth)
        self.session.auth = self.auth
        if client and self._login_check:
            self._check_login(client, retry=3)

    def _check_login(self, client=None, retry=None):
        def _raise(error):
            if retry:
                _LOGGER.warning('Retry session check (%s)', self.url)
                return self._check_login(client, retry=retry - 1)
            self.logout()
            raise error

        try:
            resp = client.get_user()
            if not resp.is_ok:
                raise NextCloudConnectionError(
                    'Failed to login to NextCloud', self.url, resp)
        except NextCloudConnectionError as nxc_error:
            if isinstance(nxc_error.obj, requests.exceptions.ConnectionError):
                time.sleep(1)  # delay on max retry cases
                _raise(nxc_error)
            elif isinstance(nxc_error.obj, requests.exceptions.SSLError):
                _raise(nxc_error)
            elif isinstance(nxc_error.obj, BaseResponse):
                if nxc_error.obj.status_code not in [
                        ExternalApiCodes.NOT_AUTHORIZED,
                        ExternalApiCodes.UNAUTHORIZED
                ]:
                    _raise(nxc_error)
            raise nxc_error
        except Exception as any_error:
            self.logout()
            raise any_error

    def logout(self):
        """Log out the authenticated user and close the session.

        :returns: True if the operation succeeded
        :raises: HTTPResponseError in case an HTTP error status was returned
        """
        if self.session:
            self.session.close()
            self.session = None
        return True

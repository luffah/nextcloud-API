# -*- coding: utf-8 -*-
""" Concrete part for managing sessions and requests """
import logging
import time
import requests
from .compat import encode_requests_password
from .codes import ExternalApiCodes
from .exceptions import (
    NextCloudConnectionError, NextCloudLoginError
)
from .response import BaseResponse

_LOGGER = logging.getLogger(__name__)


class CustomRetry(requests.packages.urllib3.util.retry.Retry):

    def get_backoff_time(self):
        return 20.0

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
        self.login_url = self.url
        session_kwargs = session_kwargs or {}
        self._login_check = session_kwargs.pop('on_session_login', False)
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
        # print(locals())
        try:
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
        # To avoid deadlocks on "Resetting dropped connection"
        adapter = requests.adapters.HTTPAdapter()
        # adapter.max_retries = CustomRetry(status_forcelist=[ 502, 503, 504 ])
        adapter.max_retries = requests.packages.urllib3.util.retry.Retry(
            status_forcelist=[ 502, 503, 504 ]
        )
        #
        self.session = requests.Session()
        #
        self.session.mount('https://', adapter)
        #
        for k in self._session_kwargs:
            setattr(self.session, k, self._session_kwargs[k])

        self._set_credentials(user, password, auth)
        self.session.auth = self.auth
        if client:
            login_check_func = self._login_check
            if isinstance(login_check_func, str):
                login_check_func = getattr(client, login_check_func)
            if self._login_check:
                self._check_login(login_check_func, retry=[20, 60, 20, 60])

    def _check_login(self, check_func, retry=None):
        # :param retry: int (number of retries) or list of int (delays)
        # There is max 6 attempts per minute before being blacklisted.
        # Source:
        #    https://help.nextcloud.com/t/master-password-retry-policy/110610
        # Approximatelly:
        #  if you wait 20 seconds, there is 1/3 chance of success
        #  if you wait 1 minute, there is 100% chance of success
        def _raise(retry, error):
            is_retriable=(
                isinstance(error.obj, requests.exceptions.ConnectionError)
                or
                isinstance(error.obj, requests.exceptions.SSLError)
                or
                isinstance(error.obj, requests.exceptions.MaxRetryError)
                or (
                    isinstance(nxc_error.obj, BaseResponse) and
                    nxc_error.obj.status_code not in [
                        ExternalApiCodes.NOT_AUTHORIZED,
                        ExternalApiCodes.UNAUTHORIZED
                    ])
            )
            if is_retriable and retry:
                delay = 10
                if isinstance(retry, list):
                    delay, retry = (retry[0], retry[1:])
                elif isinstance(retry, int):
                    retry -= 1
                else:
                    retry = False
                _LOGGER.warning('Retry session check (%s) in %s seconds',
                                self.login_url, delay)
                time.sleep(delay)
                _LOGGER.warning('Retry session check (%s)', self.login_url)
                return self._check_login(client, retry=retry)
            self.logout()
            raise error

        try:
            if not check_func().is_ok:
                raise NextCloudLoginError(
                    'Failed to login to NextCloud', self.login_url, resp)
        except NextCloudConnectionError as nxc_error:
            _raise(retry, nxc_error)
        except NextCloudLoginError as nxc_error:
            _raise(retry, nxc_error)
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

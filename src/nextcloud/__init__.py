# -*- coding: utf-8 -*-
""" Nextcloud/OwnCloud client. See NextCloud object. """
import logging
import re
from .session import Session
from .api_wrappers import API_WRAPPER_CLASSES

_LOGGER = logging.getLogger(__name__)

# pylint: disable=useless-object-inheritance
class NextCloud(object):
    """
    A NextCloud/OwnCloud client.
    Provides cookie persistence, connection-pooling, and configuration.

    Basic Usage::

      >>> from nextcloud import nextcloud
      >>> s = Nextcloud('https://nextcloud.mysite.com', user='admin', password='admin')
      >>> # or using use another auth method
      >>> from requests.auth import HTTPBasicAuth
      >>> s = Nextcloud('https://nextcloud.mysite.com', auth=HTTPBasicAuth('admin', 'admin'))
      >>> #
      >>> s.list_folders('/')
      <Response [200] data={} is_ok=True>

    For a persistent session::
      >>> s.login()  # if no user, password, or auth in parameter use existing
      >>> # some actions #
      >>> s.logout()

    Or as a context manager::

      >>> with Nextcloud('https://nextcloud.mysite.com',
      ...                user='admin', password='admin') as nxc:
      ...     # some actions #
    """

    # pylint: disable=too-many-arguments
    def __init__(self, endpoint=None,
                 user=None, password=None, auth=None,
                 session_kwargs=None,
                 session=None, **kwargs):
        if 'json_output' in kwargs:
            _LOGGER.warning(
                "'json_output' argument is deprecated :"
                " response.data will be a dict-like object if the data is compatible."
                " You can use response.json_data to be sure to get a dict."
            )

        self.session = session or Session(
            url=endpoint, user=user, password=password, auth=auth,
            session_kwargs=session_kwargs
        )
        #FIXME see base & requester
        # @FIX_API_URL fix api url for case nextcloud is not on server root {{
        url_parts = re.match(r"^((https?://)?[^/]*)(/.*)?", self.session.url)
        (server_part_url, api_url_base) = (url_parts.group(1), url_parts.group(3))
        if api_url_base:
            self.session.url = server_part_url
        # }}
        for functionality_class in API_WRAPPER_CLASSES:
            # @FIX_API_URL {{
            if not getattr(functionality_class, '_ORIG_API_URL', False):
                functionality_class._ORIG_API_URL = functionality_class.API_URL
            if api_url_base:
                functionality_class.API_URL = api_url_base + functionality_class._ORIG_API_URL
            # }}
            functionality_instance = functionality_class(self)
            for potential_method in dir(functionality_instance):
                if not potential_method.startswith('_'):
                    if not callable(getattr(functionality_instance, potential_method)):
                        pass
                    else:
                        setattr(self, potential_method, getattr(
                            functionality_instance, potential_method))

    @property
    def user(self):
        " Session User "
        return self.session.user

    @property
    def url(self):
        " Session Url "
        return self.session.url

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, *args):
        self.logout()

    def login(self, user=None, password=None, auth=None):
        " Session login() "
        self.logout()
        return self.session.login(user=user, password=password, auth=auth,
                                  client=self)

    def logout(self):
        " Session logout() "
        self.session.logout()

    def _with_auth(self, auth=None, **kwargs):
        #pylint: disable=protected-access
        init_kwargs = {'session_kwargs': self.session._session_kwargs}
        init_kwargs.update(kwargs)
        if 'endpoint' in kwargs:
            return self.__class__(auth=auth, **init_kwargs)
        return self.__class__(endpoint=self.session.url, auth=auth, **init_kwargs)

    def with_attr(self, **kwargs):
        """ Get a new client with some attribute change """
        if 'auth' in kwargs or 'endpoint' in kwargs or 'user' in kwargs:
            return self._with_auth(**kwargs)
        if 'session_kwargs' in kwargs:
            return self._with_auth(auth=self.session.auth, **kwargs)
        return self.__class__(session=self.session, **kwargs)

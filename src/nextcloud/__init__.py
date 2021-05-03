# -*- coding: utf-8 -*-
from .session import Session
from .api_wrappers import API_WRAPPER_CLASSES


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

    def __init__(self, endpoint=None,
                 user=None, password=None, json_output=True, auth=None,
                 session_kwargs=None,
                 session=None):
        self.session = session or Session(
            url=endpoint, user=user, password=password, auth=auth,
            session_kwargs=session_kwargs
        )
        self.json_output = json_output
        for functionality_class in API_WRAPPER_CLASSES:
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
        return self.session.user

    @property
    def url(self):
        return self.session.url

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, *args):
        self.logout()

    def login(self, user=None, password=None, auth=None):
        self.logout()
        return self.session.login(user=user, password=password, auth=auth,
                                  client=self)

    def with_attr(self, **kwargs):
        if 'auth' in kwargs:
            return self.with_auth(**kwargs)
        if 'session_kwargs' in kwargs:
            return self.with_auth(self.session.auth, **kwargs)
        return self.__class__(session=self.session, **kwargs)

    def with_auth(self, auth=None, **kwargs):
        init_kwargs = {'session_kwargs': self.session._session_kwargs,
                       'json_output': self.json_output}
        init_kwargs.update(kwargs)
        return self.__class__(self.session.url, auth=auth, **init_kwargs)

    def logout(self):
        if self.session.session:
            self.session.logout()

import os
import random
import string
import time
from unittest import TestCase

from nextcloud import NextCloud as _NextCloud

NEXTCLOUD_VERSION = os.environ.get('NEXTCLOUD_VERSION')
NEXTCLOUD_HOSTNAME = os.environ.get('NEXTCLOUD_HOSTNAME', 'localhost')
NEXTCLOUD_URL = ("https://{}" if '.' in NEXTCLOUD_HOSTNAME else "http://{}:80"
                 ).format(NEXTCLOUD_HOSTNAME)  # every host.domain
                                               # probably works with SSL
NEXTCLOUD_USERNAME = os.environ.get('NEXTCLOUD_ADMIN_USER', 'admin')
NEXTCLOUD_PASSWORD = os.environ.get('NEXTCLOUD_ADMIN_PASSWORD', 'admin')
NEXTCLOUD_SSL_ENABLED = os.environ.get('NEXTCLOUD_SSL_ENABLED', '1') == '1'

if not NEXTCLOUD_SSL_ENABLED:
    import urllib3
    urllib3.disable_warnings()

class NextCloud(_NextCloud):

    def __init__(self, endpoint=None, user=None, password=None,
                 session_kwargs=None, **kwargs):
        session_kwargs = session_kwargs.copy() if session_kwargs else {}
        session_kwargs.update({'verify': NEXTCLOUD_SSL_ENABLED})
        super(NextCloud, self).__init__(
            endpoint=endpoint, user=user, password=password,
            session_kwargs=session_kwargs, **kwargs
        )

class BaseTestCase(TestCase):

    SUCCESS_CODE = 100
    INVALID_INPUT_CODE = 101
    USERNAME_ALREADY_EXISTS_CODE = 102
    UNKNOWN_ERROR_CODE = 103
    NOT_FOUND_CODE = 404

    def setUp(self):
        self.username = NEXTCLOUD_USERNAME
        self.nxc = NextCloud(NEXTCLOUD_URL, NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD)
        self.nxc.login()

    def tearDown(self):
        self.nxc.logout()

    def create_new_user(self, username_prefix, password=None):
        """ Helper method to create new user """
        new_user_username = username_prefix + self.get_random_string(length=4)
        user_password = password or self.get_random_string(length=8)
        res = self.nxc.add_user(new_user_username, user_password)
        assert res.is_ok
        return new_user_username

    def delete_user(self, username):
        """ Helper method to delete user by username """
        res = self.nxc.delete_user(username)
        assert res.is_ok

    def clear(self, nxc=None, user_ids=None, group_ids=None, share_ids=None, group_folder_ids=None):
        """
        Delete created objects during tests

        Args:
            nxc (NextCloud object): (optional) Nextcloud instance, if not given - self.nxc is used
            user_ids (list): list of user ids
            group_ids (list): list of group ids
            share_ids (list): list of shares ids

        Returns:

        """
        nxc = nxc or self.nxc
        if share_ids:
            for share_id in share_ids:
                res = nxc.delete_share(share_id)
                assert res.is_ok
        if group_ids:
            for group_id in group_ids:
                res = nxc.delete_group(group_id)
                assert res.is_ok
        if user_ids:
            for user_id in user_ids:
                res = nxc.delete_user(user_id)
                assert res.is_ok
        if group_folder_ids:
            for group_folder_id in group_folder_ids:
                res = nxc.delete_group_folder(group_folder_id)
                assert res.is_ok

    def get_random_string(self, length=6):
        """ Helper method to get random string with set length  """
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


class LocalNxcUserMixin(object):
    """Mixin to create new clean NextCloud admin user for tests and delete it on tear down"""

    def setUp(self):
        super(LocalNxcUserMixin, self).setUp()
        user_password = self.get_random_string(length=8)
        self.user_username = self.create_new_user('test_user_', password=user_password)
        self.nxc_local = NextCloud(NEXTCLOUD_URL, self.user_username, user_password)
        # make user admin
        self.nxc_local.login()
        self.nxc.add_to_group(self.user_username, 'admin')

    def tearDown(self):
        self.nxc_local.logout()
        self.nxc.delete_user(self.user_username)

# -*- coding: utf-8 -*-
"""
Webdav Trashbin wrapper
See https://docs.nextcloud.com/server/14/admin_manual/configuration_user/user_auth_ldap_api.html
"""
import re
from nextcloud import base
from ..api.properties import NCProp
from . import webdav

class File(webdav.File):
    """
    Define properties on a WebDav file in trash
    """

    trashbin_filename = NCProp()
    trashbin_original_location = NCProp()
    trashbin_delection_time = NCProp()

    def delete(self):
        """
        Delete file (see WebDAVTrash wrapper)
        """
        resp = self._wrapper.delete_trashbin_file(self._get_remote_path())

        return resp.is_ok

    def restore(self):
        """
        Restore file (see WebDAVTrash wrapper)
        """
        resp = self._wrapper.restore_trashbin_file(self._get_remote_path())

        return resp.is_ok


class WebDAVTrash(base.WebDAVApiWrapper):
    """ WebDav API wrapper """
    API_URL = "/remote.php/dav/trashbin"

    def _get_path(self, operation):
        return '/'.join([self.client.user, operation]).replace('//', '/')

    def list_trashbin_files(self, all_properties=False, fields=None):
        """
        Get files list with files properties
        (for current user)

        Args:
            all_properties (bool): list all available file properties in Nextcloud
            fields (str list): file properties to fetch

        Returns:
            list of (trash) File objects
        """
        data = File.build_xml_propfind(
            use_default=all_properties,
            fields=fields
        )
        resp = self.requester.propfind(self._get_path('trash'),
                                       data=data)
        return File.from_response(resp, wrapper=self)

    def delete_trashbin_file(self, path):
        return self.requester.delete(url=self._get_path(path))

    def restore_trashbin_file(self, path):
        return self.requester.move(url=self._get_path(path),
                                   destination=self._get_path('restore'))

    def empty_trashbin(self):
        return self.requester.delete(url=self._get_path('trash'))

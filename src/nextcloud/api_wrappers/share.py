# -*- coding: utf-8 -*-
"""
Share API wrapper
See https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-share-api.html
    https://doc.owncloud.com/server/developer_manual/core/apis/ocs-share-api.html
"""
from nextcloud import base
from nextcloud.codes import ShareType


class Share(base.OCSv2ApiWrapper):
    """ Share API wrapper """
    API_URL = "/ocs/v2.php/apps/files_sharing/api/v1"
    LOCAL = "shares"

    def get_local_url(self, additional_url=""):
        if additional_url:
            return "/".join([self.LOCAL, additional_url])
        return self.LOCAL

    @staticmethod
    def validate_share_parameters(path, share_type, share_with):
        """
        Check if share parameters make sense

        Args:
            path (str): path to the file/folder which should be shared
            share_type (int): ShareType attribute
            share_with (str): user/group id with which the file should be shared

        Returns:
            bool: True if parameters make sense together, False otherwise
        """
        if (
            path is None or not isinstance(share_type, int) or (
                share_with is None and
                share_type in [ShareType.GROUP, ShareType.USER, ShareType.FEDERATED_CLOUD_SHARE]
            )
        ):
            return False
        return True

    def get_shares(self):
        """ Get all shares from the user """
        return self.requester.get(self.get_local_url())

    def get_shares_from_path(self, path, reshares=None, subfiles=None):
        """
        Get all shares from a given file/folder

        Args:
            path (str): path to file/folder
            reshares (bool): (optional) return not only the shares from the current user but
                all shares from the given file
            subfiles (bool): (optional) return all shares within a folder, given that path
                defines a folder

        Returns:
            requester response
        """
        url = self.get_local_url()
        params = {
            "path": path,
            # TODO: test reshares, subfiles
            "reshares": None if reshares is None else str(bool(reshares)).lower(),
            "subfiles": None if subfiles is None else str(bool(subfiles)).lower(),
        }
        return self.requester.get(url, params=params)

    def get_share_info(self, sid):
        """
        Get information about a given share

        Args:
            sid (int): share id

        Returns:
            requester response
        """
        return self.requester.get(self.get_local_url(sid))

    def create_share(
            self, path, share_type, share_with=None, public_upload=None,
            password=None, permissions=None):
        """
        Share a file/folder with a user/group or as public link

        Mandatory fields: share_type, path and share_with for share_type USER (0) or GROUP (1).

        Args:
            path (str): path to the file/folder which should be shared
            share_type (int): ShareType attribute
            share_with (str): user/group id with which the file should be shared
            public_upload (bool): bool, allow public upload to a public shared folder (true/false)
            password (str): password to protect public link Share with
            permissions (int): sum of selected Permission attributes

        Returns:
            requester response
        """
        if not self.validate_share_parameters(path, share_type, share_with):
            return False

        url = self.get_local_url()
        if public_upload:
            public_upload = "true"

        data = {"path": path, "shareType": share_type}
        if share_type in [ShareType.GROUP, ShareType.USER, ShareType.FEDERATED_CLOUD_SHARE]:
            data["shareWith"] = share_with
        if public_upload:
            data["publicUpload"] = public_upload
        if share_type == ShareType.PUBLIC_LINK and password is not None:
            data["password"] = str(password)
        if permissions is not None:
            data["permissions"] = permissions
        return self.requester.post(url, data)

    def delete_share(self, sid):
        """
        Remove the given share

        Args:
            sid (str): share id

        Returns:
            requester response
        """
        return self.requester.delete(self.get_local_url(sid))

    def update_share(self, sid,
                     permissions=None, password=None, public_upload=None, expire_date=""):
        """
        Update a given share, only one value can be updated per request

        Args:
            sid (str): share id
            permissions (int): sum of selected Permission attributes
            password (str): password to protect public link Share with
            public_upload (bool): bool, allow public upload to a public shared folder (true/false)
            expire_date (str): set an expire date for public link shares. Format: ‘YYYY-MM-DD’

        Returns:
            requester response
        """
        params = dict(
            permissions=permissions,
            password=password,
            expireDate=expire_date
        )
        if public_upload:
            params["publicUpload"] = "true"
        if public_upload is False:
            params["publicUpload"] = "false"

        # check if only one param specified
        specified_params_count = sum([int(bool(each)) for each in params.values()])
        if specified_params_count > 1:
            raise ValueError("Only one parameter for update can be specified per request")

        url = self.get_local_url(sid)
        return self.requester.put(url, data=params)

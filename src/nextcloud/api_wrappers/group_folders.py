# -*- coding: utf-8 -*-
"""
GroupFolders API wrapper
See https://github.com/nextcloud/groupfolders
    https://apps.nextcloud.com/apps/groupfolders
"""
from nextcloud import base


class GroupFolders(base.OCSv1ApiWrapper):
    """ GroupFolders API wrapper """

    API_URL = "/apps/groupfolders/folders"
    JSON_ABLE = False

    def get_group_folders(self):
        """
        Return a list of call configured folders and their settings

        :returns:  resquester response
        """
        return self.requester.get()

    def get_group_folder(self, fid):
        """
        Return a specific configured folder and it's settings

        :param fid (int/str): group folder id
        :returns:  resquester response
        """
        return self.requester.get(fid)

    def create_group_folder(self, mountpoint):
        """
        Create a new group folder

        :param mountpoint (str): name for the new folder
        :returns:  resquester response
        """
        return self.requester.post(data={"mountpoint": mountpoint})

    def delete_group_folder(self, fid):
        """
        Delete a group folder

        :param fid (int/str): group folder id
        :returns:  resquester response
        """
        return self.requester.delete(fid)

    def grant_access_to_group_folder(self, fid, gid):
        """
        Give a group access to a folder

        :param fid (int/str): group folder id
        :returns:  resquester response
        """
        url = "/".join([str(fid), "groups"])
        return self.requester.post(url, data={"group": gid})

    def revoke_access_to_group_folder(self, fid, gid):
        """
        Remove access from a group to a folder

        :param fid (int/str): group folder id
        :param gid (str): group id
        :returns:  resquester response
        """
        url = "/".join([str(fid), "groups", gid])
        return self.requester.delete(url)

    def set_permissions_to_group_folder(self, fid, gid, permissions):
        """
        Set the permissions a group has in a folder

        :param fid (int/str): group folder id
        :param gid (str): group id
        :param permissions (int): The new permissions for the group as attribute of Permission class
        :returns:  resquester response
        """
        url = "/".join([str(fid), "groups", gid])
        return self.requester.post(url, data={"permissions": permissions})

    def set_quota_of_group_folder(self, fid, quota):
        """
        Set the quota for a folder in bytes

        :param fid (int/str): group folder id
        :param quota (int/str): The new quota for the folder in bytes, user -3 for unlimited
        :returns:  resquester response
        """
        url = "/".join([str(fid), "quota"])
        return self.requester.post(url, data={"quota": quota})

    def rename_group_folder(self, fid, mountpoint):
        """
        Change the name of a folder

        :param fid (int/str): group folder id
        :param mountpoint (str): name for the new folder
        :returns:  resquester response
        """
        url = "/".join([str(fid), "mountpoint"])
        return self.requester.post(url, data={"mountpoint": mountpoint})

    def toggle_acl(self, fid, acl=1):
        """
        Enable∕disable advanced ACL on given group folder

        :param fid (int/str): group folder id
        :param acl (int): 1 for enable, 0 for disable
        """
        url = "/".join([str(fid), "acl"])
        return self.requester.post(url, data={"acl": acl})

    def manage_acl(self, fid, mapping_id, mapping_type="user", manage_acl=1):
        """
        Grant/Remove a group or user the ability to manage a groupfolders' advanced permissions

        :param fid (int/str): group folder id
        :param mapping_id (str): user id or group id
        :param mapping_type (str): "user" or "group"
        :param manage_acl (int): 0 to delete ACL, 1 to add ACL
        :returns:  requester response
        """
        url = "/".join([str(fid), "manageACL"])
        data = {
            "mappingType": mapping_type,
            "manageAcl": manage_acl,
            "mappingId": mapping_id,
        }
        return self.requester.post(url, data=data)

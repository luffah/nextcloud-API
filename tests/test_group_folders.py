# -*- coding: utf-8 -*-
from nextcloud.codes import Permission, QUOTA_UNLIMITED

from .base import BaseTestCase


class TestGroupFolders(BaseTestCase):

    def setUp(self):
        super(TestGroupFolders, self).setUp()
        self.nxc.enable_app('groupfolders')

    def test_crud_group_folder(self):
        # create new group folder
        folder_mount_point = "test_group_folders_" + self.get_random_string(length=4)
        res = self.nxc.create_group_folder(folder_mount_point)
        assert res.is_ok
        group_folder_id = res.data['id']

        # get all group folders and check if just created folder is in the list
        res = self.nxc.get_group_folders()
        assert res.is_ok
        group_folders = res.data
        assert str(group_folder_id) in group_folders
        assert group_folders[str(group_folder_id)]['mount_point'] == folder_mount_point

        # retrieve single folder
        res = self.nxc.get_group_folder(group_folder_id)
        assert res.is_ok
        assert str(res.data['id']) == str(group_folder_id)
        assert res.data['mount_point'] == folder_mount_point

        # rename group folder
        new_folder_mount_point = folder_mount_point + '_new'
        res = self.nxc.rename_group_folder(group_folder_id, new_folder_mount_point)
        assert res.is_ok and res.data is True
        # check if name was changed
        res = self.nxc.get_group_folder(group_folder_id)
        assert res.data['mount_point'] == new_folder_mount_point

        # delete group folder
        res = self.nxc.delete_group_folder(group_folder_id)
        assert res.is_ok
        assert res.data is True
        # check that deleted folder isn't retrieved
        res = self.nxc.get_group_folder(group_folder_id)
        assert res.is_ok
        assert res.data is False

    def test_grant_revoke_access_to_group_folder(self):
        # create group to share with
        group_id = 'test_folders_' + self.get_random_string(length=4)
        self.nxc.add_group(group_id)

        # create new group folder
        folder_mount_point = "test_access_" + self.get_random_string(length=4)
        res = self.nxc.create_group_folder(folder_mount_point)
        assert res.is_ok
        group_folder_id = res.data['id']

        # assert that no groups have access to just created folder
        res = self.nxc.get_group_folder(group_folder_id)
        assert res.is_ok
        assert len(res.data['groups']) == 0

        # grant access to group
        res = self.nxc.grant_access_to_group_folder(group_folder_id, group_id)
        assert res.is_ok
        assert res.data is True

        # check that folder has this group
        res = self.nxc.get_group_folder(group_folder_id)
        assert res.data['groups'] == {group_id: Permission.ALL}

        # revoke access
        res = self.nxc.revoke_access_to_group_folder(group_folder_id, group_id)
        assert res.is_ok
        assert res.data is True

        # check that folder has no groups again
        res = self.nxc.get_group_folder(group_folder_id)
        assert len(res.data['groups']) == 0

        # clear
        self.clear(nxc=self.nxc, group_ids=[group_id], group_folder_ids=[group_folder_id])

    def test_setting_folder_quotas(self):
        # create new group folder
        folder_mount_point = "test_folder_quotas_" + self.get_random_string(length=4)
        res = self.nxc.create_group_folder(folder_mount_point)
        assert res.is_ok
        group_folder_id = res.data['id']

        # assert quota is unlimited by default
        res = self.nxc.get_group_folder(group_folder_id)
        assert res.is_ok
        assert int(res.data['quota']) == QUOTA_UNLIMITED

        # set quota
        QUOTA_ONE_GB = 1024 * 1024 * 1024
        res = self.nxc.set_quota_of_group_folder(group_folder_id, QUOTA_ONE_GB)
        assert res.is_ok and res.data is True
        # check if quota changed
        res = self.nxc.get_group_folder(group_folder_id)
        assert res.is_ok
        assert str(res.data['quota']) == str(QUOTA_ONE_GB)

        # clear
        self.clear(group_folder_ids=[group_folder_id])

    def test_setting_folder_permissions(self):
        # create group to share with
        group_id = 'test_folders_' + self.get_random_string(length=4)
        self.nxc.add_group(group_id)

        # create new group folder
        folder_mount_point = "test_folder_permissions_" + self.get_random_string(length=4)
        res = self.nxc.create_group_folder(folder_mount_point)
        assert res.is_ok
        group_folder_id = res.data['id']

        # add new group to folder
        self.nxc.grant_access_to_group_folder(group_folder_id, group_id)
        # assert permissions is ALL by default
        res = self.nxc.get_group_folder(group_folder_id)
        assert int(res.data['quota']) == QUOTA_UNLIMITED

        # set permissions
        new_permission = Permission.READ + Permission.CREATE
        res = self.nxc.set_permissions_to_group_folder(group_folder_id, group_id, new_permission)
        assert res.is_ok
        assert res.data is True
        # check if permissions changed
        res = self.nxc.get_group_folder(group_folder_id)
        assert str(res.data['groups'][group_id]) == str(new_permission)

        # clear
        self.clear(nxc=self.nxc, group_ids=[group_id], group_folder_ids=[group_folder_id])

    def test_grant_revoke_advanced_acl_to_user(self):
        # create group to share with
        group_id = 'test_folders_' + self.get_random_string(length=4)
        self.nxc.add_group(group_id)

        # create a user to manage advanced permissions
        username = self.create_new_user("folder_manager")

        # create new group folder
        folder_mount_point = "test_folder_advanced_permissions_" + self.get_random_string(length=4)
        res = self.nxc.create_group_folder(folder_mount_point)
        assert res.is_ok
        group_folder_id = res.data['id']

        # add new group to folder
        self.nxc.grant_access_to_group_folder(group_folder_id, group_id)
        # assert permissions is ALL by default
        res = self.nxc.get_group_folder(group_folder_id)
        assert int(res.data['quota']) == QUOTA_UNLIMITED

        # grant advanced ACL
        self.nxc.manage_acl(group_folder_id, username)
        # XXX We have to wait for commit https://github.com/nextcloud/groupfolders/commit/1c3874e0b980
        #res = self.nxc.get_group_folder(group_folder_id)
        # assert username in res.data["manage"]
        res = self.nxc.get_group_folders()
        assert str(group_folder_id) in res.data
        assert username in res.data[str(group_folder_id)]["manage"]
        assert res.data[str(group_folder_id)]["manage"][username]["type"] == "user"

        # revoke advanced ACL
        self.nxc.manage_acl(group_folder_id, username, manage_acl=0)
        # XXX We have to wait for commit https://github.com/nextcloud/groupfolders/commit/1c3874e0b980
        #res = self.nxc.get_group_folder(group_folder_id)
        # assert username not in res.data["manage"]
        res = self.nxc.get_group_folders()
        assert str(group_folder_id) in res.data
        assert username not in res.data[str(group_folder_id)]["manage"]

        # clear
        self.clear(nxc=self.nxc, group_ids=[group_id], group_folder_ids=[group_folder_id])

    def test_grant_revoke_advanced_acl_to_group(self):
        # create group to share with
        group_id = 'test_folders_' + self.get_random_string(length=4)
        self.nxc.add_group(group_id)

        # create a second group to manage advanced permissions
        admin_group_id = 'admin_group_' + self.get_random_string(length=4)
        self.nxc.add_group(admin_group_id)

        # create new group folder
        folder_mount_point = "test_folder_advanced_permissions_" + self.get_random_string(length=4)
        res = self.nxc.create_group_folder(folder_mount_point)
        assert res.is_ok
        group_folder_id = res.data['id']

        # add new group to folder
        self.nxc.grant_access_to_group_folder(group_folder_id, group_id)
        # assert permissions is ALL by default
        res = self.nxc.get_group_folder(group_folder_id)
        assert int(res.data['quota']) == QUOTA_UNLIMITED

        # grant advanced ACL
        self.nxc.manage_acl(group_folder_id, admin_group_id, mapping_type="group")
        # XXX We have to wait for commit https://github.com/nextcloud/groupfolders/commit/1c3874e0b980
        #res = self.nxc.get_group_folder(group_folder_id)
        # assert admin_group_id in res.data["manage"]
        res = self.nxc.get_group_folders()
        assert str(group_folder_id) in res.data
        assert admin_group_id in res.data[str(group_folder_id)]["manage"]
        assert res.data[str(group_folder_id)]["manage"][admin_group_id]["type"] == "group"

        # revoke advanced ACL
        self.nxc.manage_acl(group_folder_id, admin_group_id, mapping_type="group", manage_acl=0)
        # XXX We have to wait for commit https://github.com/nextcloud/groupfolders/commit/1c3874e0b980
        #res = self.nxc.get_group_folder(group_folder_id)
        # assert admin_group_id not in res.data["manage"]
        res = self.nxc.get_group_folders()
        assert str(group_folder_id) in res.data
        assert admin_group_id not in res.data[str(group_folder_id)]["manage"]

        # clear
        self.clear(nxc=self.nxc, group_ids=[group_id], group_folder_ids=[group_folder_id])

    def test_toggle_advanced_acl(self):
        # create group to share with
        group_id = 'test_folders_' + self.get_random_string(length=4)
        self.nxc.add_group(group_id)

        # create new group folder
        folder_mount_point = "test_folder_advanced_permissions_" + self.get_random_string(length=4)
        res = self.nxc.create_group_folder(folder_mount_point)
        assert res.is_ok
        group_folder_id = res.data['id']

        # add new group to folder
        self.nxc.grant_access_to_group_folder(group_folder_id, group_id)
        # assert permissions is ALL by default
        res = self.nxc.get_group_folder(group_folder_id)
        assert int(res.data['quota']) == QUOTA_UNLIMITED

        self.nxc.toggle_acl(group_folder_id, acl=1)
        # XXX We have to wait for commit https://github.com/nextcloud/groupfolders/commit/1c3874e0b980
        #res = self.nxc.get_group_folder(group_folder_id)
        # assert admin_group_id not in res.data["manage"]
        res = self.nxc.get_group_folders()
        assert str(group_folder_id) in res.data
        assert "1" in res.data[str(group_folder_id)]["acl"]

        self.nxc.toggle_acl(group_folder_id, acl=0)
        # XXX We have to wait for commit https://github.com/nextcloud/groupfolders/commit/1c3874e0b980
        #res = self.nxc.get_group_folder(group_folder_id)
        # assert admin_group_id not in res.data["manage"]
        res = self.nxc.get_group_folders()
        assert str(group_folder_id) in res.data
        assert "1" not in res.data[str(group_folder_id)]["acl"]

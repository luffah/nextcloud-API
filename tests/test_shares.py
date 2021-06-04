# -*- coding: utf-8 -*-
import requests
from datetime import datetime, timedelta

from nextcloud.codes import ShareType, Permission
from nextcloud.common.timestamping import datetime_to_expire_date

from .base import BaseTestCase, LocalNxcUserMixin


class TestShares(LocalNxcUserMixin, BaseTestCase):

    def test_share_create_retrieve_delete(self):
        """ shallow test for base retrieving single, list, creating and deleting share """
        # check no shares exists
        res = self.nxc_local.get_shares()
        assert res.is_ok
        assert len(res.data) == 0

        # create public share
        res = self.nxc_local.create_share('Documents', share_type=ShareType.PUBLIC_LINK)
        assert res.is_ok
        share_id = res.data['id']

        # get all shares
        all_shares = self.nxc_local.get_shares().data
        assert len(all_shares) == 1
        assert all_shares[0]['id'] == share_id
        assert all_shares[0]['share_type'] == ShareType.PUBLIC_LINK

        # get single share info
        created_share = self.nxc_local.get_share_info(share_id)
        assert res.is_ok
        created_share_data = created_share.data[0]
        assert created_share_data['id'] == share_id
        assert created_share_data['share_type'] == ShareType.PUBLIC_LINK
        assert created_share_data['uid_owner'] == self.user_username

        # delete share
        res = self.nxc_local.delete_share(share_id)
        assert res.is_ok
        all_shares = self.nxc_local.get_shares().data
        assert len(all_shares) == 0

    def test_create(self):
        """ creating share with different params """
        share_path = "Documents"
        user_to_share_with = self.create_new_user("test_shares_")
        group_to_share_with = 'group_to_share_with'
        self.nxc.add_group(group_to_share_with)

        # create for user, group
        for (share_type, share_with, permissions) in [(ShareType.USER, user_to_share_with, Permission.READ),
                                                      (ShareType.GROUP, group_to_share_with, Permission.READ + Permission.CREATE)]:
            # create share with user
            res = self.nxc_local.create_share(share_path,
                                              share_type=share_type,
                                              share_with=share_with,
                                              permissions=permissions)
            assert res.is_ok
            share_id = res.data['id']

            # check if shared with right user/group, permission
            created_share = self.nxc_local.get_share_info(share_id)
            assert res.is_ok
            created_share_data = created_share.data[0]
            assert created_share_data['id'] == share_id
            assert created_share_data['share_type'] == share_type
            assert created_share_data['share_with'] == share_with
            assert created_share_data['permissions'] == permissions

            # delete share, user
            self.nxc_local.delete_share(share_id)
            self.nxc.delete_user(user_to_share_with)

    def test_create_with_password(self):
        share_path = "Documents"
        res = self.nxc_local.create_share(path=share_path,
                                          share_type=ShareType.PUBLIC_LINK,
                                          password=self.get_random_string(length=8))
        assert res.is_ok
        share_url = res.data['url']
        share_resp = requests.get(share_url)
        assert "This share is password-protected" in share_resp.text
        self.nxc_local.delete_share(res.data['id'])

    def test_get_path_shares(self):
        share_path = "Documents"
        group_to_share_with_name = self.get_random_string(length=4) + "_test_add"
        self.nxc.add_group(group_to_share_with_name)

        # check that path has no shares yet
        res = self.nxc_local.get_shares_from_path(share_path)
        assert res.is_ok
        assert len(res.data) == 0

        # first path share
        first_share = self.nxc_local.create_share(path=share_path,
                                                  share_type=ShareType.PUBLIC_LINK)

        # create second path share
        second_share = self.nxc_local.create_share(path=share_path,
                                                   share_type=ShareType.GROUP,
                                                   share_with=group_to_share_with_name,
                                                   permissions=Permission.READ)

        all_shares_ids = [first_share.data['id'], second_share.data['id']]

        # check that path has two shares
        res = self.nxc_local.get_shares_from_path(share_path)
        assert res.is_ok
        assert len(res.data) == 2
        assert all([each['id'] in all_shares_ids for each in res.data])

        # clean shares, groups
        self.clear(self.nxc_local, share_ids=all_shares_ids, group_ids=[group_to_share_with_name])

    def test_update_share(self):
        share_path = "Documents"
        user_to_share_with = self.create_new_user("test_shares_")

        share_with = user_to_share_with
        share_type = ShareType.USER
        # create share with user
        res = self.nxc_local.create_share(share_path,
                                          share_type=ShareType.USER,
                                          share_with=user_to_share_with,
                                          permissions=Permission.READ)
        assert res.is_ok
        share_id = res.data['id']

        # update share permissions
        new_permissions = Permission.READ + Permission.CREATE
        res = self.nxc_local.update_share(share_id, permissions=new_permissions)
        assert res.is_ok

        updated_share_data = res.data
        assert updated_share_data['id'] == share_id
        assert updated_share_data['share_type'] == share_type
        assert updated_share_data['share_with'] == share_with
        assert updated_share_data['permissions'] == new_permissions
        assert updated_share_data['expiration'] is None

        # update share expire date
        expire_date = datetime_to_expire_date(datetime.now() + timedelta(days=5))
        res = self.nxc_local.update_share(share_id, expire_date=expire_date)
        assert res.is_ok

        updated_share_data = res.data
        assert updated_share_data['id'] == share_id
        assert updated_share_data['share_type'] == share_type
        assert updated_share_data['share_with'] == share_with
        assert updated_share_data['permissions'] == new_permissions
        assert updated_share_data['expiration'] == "{} 00:00:00".format(expire_date)

        self.clear(self.nxc_local, share_ids=[share_id], user_ids=[user_to_share_with])

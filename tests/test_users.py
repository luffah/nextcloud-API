# -*- coding: utf-8 -*-
from .base import BaseTestCase


class TestUsers(BaseTestCase):

    def test_get_users(self):
        res = self.nxc.get_users()
        assert res.is_ok
        assert len(res.data['users']) > 0
        # test search argument
        res = self.nxc.get_users(search=self.username)
        users = res.data['users']
        assert all([self.username in user for user in users])
        # test limit argument
        res = self.nxc.get_users(limit=0)
        assert len(res.data['users']) == 0

    def test_get_user(self):
        res = self.nxc.get_user(self.username)
        assert res.is_ok
        user = res.data
        assert user['id'] == self.username
        assert user['enabled']

    def test_add_user(self):
        new_user_username = self.get_random_string(length=4) + "test_add"
        res = self.nxc.add_user(new_user_username, self.get_random_string(length=8))
        assert res.is_ok
        added_user = self.nxc.get_user(new_user_username).data
        assert added_user['id'] == new_user_username and added_user['enabled']
        # adding same user will fail
        res = self.nxc.add_user(new_user_username, "test_password_123")
        assert res.status_code == self.USERNAME_ALREADY_EXISTS_CODE

    def test_disable_enable_user(self):
        new_user_username = self.get_random_string(length=4) + "test_enable"
        self.nxc.add_user(new_user_username, self.get_random_string(length=8))
        user = self.nxc.get_user(new_user_username).data
        assert user['enabled']
        self.nxc.disable_user(new_user_username)
        user = self.nxc.get_user(new_user_username).data
        assert not user['enabled']
        self.nxc.enable_user(new_user_username)
        user = self.nxc.get_user(new_user_username).data
        assert user['enabled']

    def test_delete_user(self):
        new_user_username = self.get_random_string(length=4) + "test_enable"
        self.nxc.add_user(new_user_username, self.get_random_string(length=8))
        res = self.nxc.delete_user(new_user_username)
        assert res.is_ok
        user_res = self.nxc.get_user(new_user_username)
        assert user_res.status_code == self.NOT_FOUND_CODE

    def test_edit_user(self):
        new_user_username = self.create_new_user("edit_user")
        new_user_values = {
            "email": "test@test.test",
            # "quota": "100MB", FIXME: only admins (of a group?) can edit quota
            "phone": "+380999999999",
            "address": "World!",
            "website": "example.com",
            "twitter": "@twitter_account",
            "displayname": "test user!",
            "password": self.get_random_string(length=10)
        }
        for key, value in new_user_values.items():
            res = self.nxc.edit_user(new_user_username, key, value)
            assert res.is_ok

    def test_resend_welcome_mail(self):
        # TODO: add mock of SMTP data to test this method
        pass


class TestUserGroups(BaseTestCase):

    def setUp(self):
        super(TestUserGroups, self).setUp()
        self.user_username = self.create_new_user('user_group_')
        # create group
        self.group_name = self.get_random_string(length=4) + "_user_groups"
        self.nxc.add_group(self.group_name)

    def tearDown(self):
        self.delete_user(self.user_username)
        self.nxc.delete_group(self.group_name)
        super(TestUserGroups, self).tearDown()

    def test_add_remove_user_from_group(self):
        # add to group
        res = self.nxc.add_to_group(self.user_username, self.group_name)
        assert res.is_ok
        group_members = self.nxc.get_group(self.group_name).data['users']
        assert self.user_username in group_members
        # remove from group
        res = self.nxc.remove_from_group(self.user_username, self.group_name)
        assert res.is_ok
        group_members = self.nxc.get_group(self.group_name).data['users']
        assert self.user_username not in group_members

    def test_create_retrieve_delete_subadmin(self):
        # promote to subadmin
        res = self.nxc.create_subadmin(self.user_username, self.group_name)
        assert res.is_ok
        # get subadmin groups
        subadmin_groups = self.nxc.get_subadmin_groups(self.user_username)
        assert subadmin_groups.is_ok
        assert self.group_name in subadmin_groups.data
        # demote from subadmin
        res = self.nxc.remove_subadmin(self.user_username, self.group_name)
        assert res.is_ok
        subadmin_groups = self.nxc.get_subadmin_groups(self.user_username).data
        assert self.group_name not in subadmin_groups

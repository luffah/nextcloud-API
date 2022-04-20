# -*- coding: utf-8 -*-

from .base import BaseTestCase


class TestSharees(BaseTestCase):

    USERNAME_PREFIX = "test_sharees_user"

    def test_search_sharees(self):
        # create a user we can search for
        sharee_user = self.create_new_user(self.USERNAME_PREFIX)

        # query the sharees api using only the username prefix
        res = self.nxc.search_sharees(self.USERNAME_PREFIX)
        assert res.is_ok
        assert "users" in res

        # check if the full username is listed in the results
        found = False
        for user in res["users"]:
            assert "label" in user
            if user["label"] == sharee_user:
                found = True
                break
        assert found

        # remove the previously created user
        self.remove_user(sharee_user)

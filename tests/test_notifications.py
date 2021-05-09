# -*- coding: utf-8 -*-
from .base import BaseTestCase


class TestNotifications(BaseTestCase):

    def test_get_delete_notifications(self):
        # get all notifications
        res = self.nxc.get_notifications()
        all_data = res.data
        assert res.is_ok

        if all_data:
            notification = all_data[0]

            # get single notification
            res = self.nxc.get_notification(notification['notification_id'])
            assert res.is_ok
            assert res.data['notification_id'] == notification['notification_id']

            # delete single notification
            res = self.nxc.delete_notification(notification['notification_id'])
            assert res.is_ok
        else:
            # assert get single notification will return 404 not found
            res = self.nxc.get_notification(1)
            assert res.status_code == self.NOT_FOUND_CODE

        # delete all notifications success code check
        res = self.nxc.delete_all_notifications()
        assert res.is_ok

        # TODO: add more tests if WebDAV api will be implemented and there will be ability to make actions
        #  using api which creates notifications (mentions in comments)
        #  or when Federated file sharings api will be implemented (harder way)

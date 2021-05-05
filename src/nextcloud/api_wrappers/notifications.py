# -*- coding: utf-8 -*-
"""
Notification API wrapper
See https://github.com/nextcloud/notifications/
    https://doc.owncloud.com/server/developer_manual/core/apis/ocs-notification-endpoint-v1.html
    https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-api-overview.html?highlight=notification#notifications
"""
from nextcloud import base


class Notifications(base.OCSv2ApiWrapper):
    """ Notification API wrapper """
    API_URL = "/ocs/v2.php/apps/notifications/api/v2/notifications"

    def get_notifications(self):
        """ Get list of notifications for a logged in user """
        return self.requester.get()

    def get_notification(self, notification_id):
        """
        Get single notification by id for a user

        :param notification_id (int): Notification id
        :returns: requester response
        """
        return self.requester.get(url=notification_id)

    def delete_notification(self, notification_id):
        """
        Delete single notification by id for a user

        :param notification_id (int): Notification id
        :returns: requester response
        """
        return self.requester.delete(url=notification_id)

    def delete_all_notifications(self):
        """ Delete all notification for a logged in user

        Notes:
            This endpoint was added for Nextcloud 14
        """
        return self.requester.delete()

# -*- coding: utf-8 -*-
"""
Apps API wrapper
See https://docs.nextcloud.com/server/14/admin_manual/configuration_user/instruction_set_for_users.html
    https://docs.nextcloud.com/server/14/admin_manual/configuration_user/user_provisioning_api.html
    https://doc.owncloud.com/server/developer_manual/core/apis/provisioning-api.html
"""
from nextcloud import base


class Apps(base.ProvisioningApiWrapper):
    API_URL = "/ocs/v1.php/cloud/apps"

    def get_apps(self, filter=None):
        """
        Get a list of apps installed on the Nextcloud server

        :param filter: str, optional "enabled" or "disabled"
        :return: OCSResponse
        """
        params = {
            "filter": filter
        }
        return self.requester.get(params=params)

    def get_app(self, app_id):
        """
        Provide information on a specific application

        :param app_id: str, app id
        :return: OCSResponse
        """
        return self.requester.get(app_id)

    def enable_app(self, app_id):
        """
        Enable an app

        :param app_id: str, app id
        :return: OCSResponse
        """
        return self.requester.post(app_id)

    def disable_app(self, app_id):
        """
        Disable the specified app

        :param app_id: str, app id
        :return: OCSResponse
        """
        return self.requester.delete(app_id)

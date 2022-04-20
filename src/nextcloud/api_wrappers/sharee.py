# -*- coding utf-8 -*-
"""
Sharee API wrapper
See https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-sharee-api.html
    https://doc.owncloud.com/server/10.8/developer_manual/core/apis/ocs-recipient-api.html
"""

from nextcloud import base

class Sharee(base.OCSv1ApiWrapper):
    """ Sharee API wrapper"""
    API_URL = "/ocs/v1.php/apps/files_sharing/api/v1"
    LOCAL = "sharees"

    def get_local_url(self):
        return self.LOCAL


    def search_sharees(self, search, lookup=False, perPage=None, itemType="file"):
        url = self.get_local_url()
        data = {
            "search": search,
            "itemType": itemType
        }

        if lookup:
            data["lookup"] = "true"
        if perPage is not None:
            data["perPage"] = perPage

        return self.requester.get(self.get_local_url(), params=data)

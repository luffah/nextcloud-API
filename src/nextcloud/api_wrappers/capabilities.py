# -*- coding: utf-8 -*-
"""
Capabilities API wrapper
See https://docs.nextcloud.com/server/14/developer_manual/client_apis/OCS/index.html#capabilities-api
    https://doc.owncloud.com/server/developer_manual/core/apis/ocs-capabilities.html
"""
from nextcloud import base


class Capabilities(base.OCSv1ApiWrapper):
    """ Capabilities API wrapper """
    API_URL = "/ocs/v1.php/cloud/capabilities"

    def get_capabilities(self):
        """ Obtain capabilities provided by the Nextcloud server and its apps """
        return self.requester.get()

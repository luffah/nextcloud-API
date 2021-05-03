# -*- coding: utf-8 -*-
"""
Capabilities API wrapper
See https://doc.owncloud.com/server/developer_manual/core/apis/ocs-capabilities.html
"""
from nextcloud import base


class Capabilities(base.OCSv1ApiWrapper):
    """ Capabilities API wrapper """
    API_URL = "/ocs/v1.php/cloud/capabilities"

    def get_capabilities(self):
        """ Obtain capabilities provided by the Nextcloud server and its apps """
        return self.requester.get()

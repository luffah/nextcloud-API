# -*- coding: utf-8 -*-
"""
Capabilities API wrapper
See https://docs.nextcloud.com/server/14/developer_manual/client_apis/OCS/index.html#capabilities-api
    https://doc.owncloud.com/server/developer_manual/core/apis/ocs-capabilities.html
"""
from .. import base

# # 2021/05/24 luffah: here the way to make an object version of the result
#
# from ..api.model import Item
# from ..api.properties import Property
#
# def _extract_major_version(vals):
#     return int(vals.get('major', 0))
#
# class CapabilitiesItem(Item):
#
#     version = Property()
#     capabilities = Property()
#
#     major_version = Property(json='version',
#                              parse_json_value=_extract_major_version)
#
#     def __get_repr_info__(self):
#         return "{'version': '%s', 'capabilities': %s}" % (
#             self.version['string'],
#             repr([k for k in self.capabilities])
#         )


class Capabilities(base.OCSv1ApiWrapper):
    """ Capabilities API wrapper """
    API_URL = "/ocs/v1.php/cloud/capabilities"

    def get_capabilities(self):
        """ Obtain capabilities provided by the Nextcloud server and its apps """
        # return CapabilitiesItem.from_response(self.requester.get())
        return self.requester.get()

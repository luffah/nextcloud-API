# -*- coding: utf-8 -*-
"""
Federated Cloud Share wrapper.
See https://doc.owncloud.com/server/developer_manual/core/apis/ocs-share-api.html#federated-cloud-shares
"""
from nextcloud import base


class FederatedCloudShare(base.OCSv2ApiWrapper):
    """ Federated Cloud Share wrapper """
    API_URL = "/ocs/v2.php/apps/files_sharing/api/v1"
    FEDERATED = "remote_shares"

    def get_federated_url(self, additional_url=""):
        if additional_url:
            return "/".join([self.FEDERATED, additional_url])
        return self.FEDERATED

    def list_accepted_federated_cloudshares(self):
        url = self.get_federated_url()
        return self.requester.get(url)

    def get_known_federated_cloudshare(self, sid):
        url = self.get_federated_url(sid)
        return self.requester.get(url)

    def delete_accepted_federated_cloudshare(self, sid):
        url = self.get_federated_url(sid)
        return self.requester.delete(url)

    def list_pending_federated_cloudshares(self):
        url = self.get_federated_url("pending")
        return self.requester.get(url)

    def accept_pending_federated_cloudshare(self, sid):
        url = self.get_federated_url("pending/{sid}".format(sid=sid))
        return self.requester.post(url)

    def decline_pending_federated_cloudshare(self, sid):
        url = self.get_federated_url("pending/{sid}".format(sid=sid))
        return self.requester.delete(url)

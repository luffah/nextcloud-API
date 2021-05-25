# -*- coding: utf-8 -*-
"""
User API wrapper
See https://docs.nextcloud.com/server/14/admin_manual/configuration_user/instruction_set_for_users.html
    https://docs.nextcloud.com/server/14/admin_manual/configuration_user/user_provisioning_api.html
    https://doc.owncloud.com/server/developer_manual/core/apis/provisioning-api.html
"""
from nextcloud import base


class User(base.ProvisioningApiWrapper):
    """ User API wrapper """
    API_URL = "/ocs/v1.php/cloud/users"

    def add_user(self, uid, passwd):
        """
        Create a new user on the Nextcloud server

        :param uid: str, uid of new user
        :param passwd: str, password of new user
        :returns:  resquester response
        """
        msg = {'userid': uid, 'password': passwd}
        return self.requester.post(data=msg)

    def get_users(self, search=None, limit=None, offset=None):
        """
        Retrieve a list of users from the Nextcloud server

        :param search: string, optional search string
        :param limit: int, optional limit value
        :param offset: int, optional offset value
        :returns:  resquester response
        """
        params = {
            'search': search,
            'limit': limit,
            'offset': offset
        }
        return self.requester.get(params=params)

    def get_user(self, uid=None):
        """
        Retrieve information about a single user

        :param uid: str, uid of user (default: current user)
        :returns:  resquester response
        """
        return self.requester.get(uid or self.client.user)

    def get_connection_issues(self):
        """
        Return Falsy falue if everything is OK, or string representing
        the connection problem (bad hostname, password, whatever)
        """
        try:
            response = self.get_user()
        except Exception as e:
            return str(e)

        if not response.is_ok:
            return response.meta['message']
        return None

    def edit_user(self, uid, what, value):
        """
        Edit attributes related to a user

        Users are able to edit email, displayname and password; admins can also edit the
        quota value

        :param uid: str, uid of user
        :param what: str, the field to edit
        :param value: str, the new value for the field
        :returns:  resquester response
        """
        keys = [
            'email', 'quota', 'phone', 'address', 'website', 'twitter',
            'displayname', 'password'
        ]
        assert what in keys, (
            "You have chosen to edit user's '{what}', but you can choose only from: {choices}"
            .format(what=what, choices=(keys()))
        )
        return self.requester.put(uid, data=dict(key=what, value=value))

    def disable_user(self, uid):
        """
        Disable a user on the Nextcloud server so that the user cannot login anymore

        :param uid: str, uid of user
        :returns:  resquester response
        """
        return self.requester.put("{uid}/disable".format(uid=uid))

    def enable_user(self, uid):
        """
        Enable a user on the Nextcloud server so that the user can login again

        :param uid: str, uid of user
        :returns:  resquester response
        """
        return self.requester.put("{uid}/enable".format(uid=uid))

    def delete_user(self, uid):
        """
        Delete a user from the Nextcloud server

        :param uid: str, uid of user
        :returns:  resquester response
        """
        return self.requester.delete("{uid}".format(uid=uid))

    def add_to_group(self, uid, gid):
        """
        Add the specified user to the specified group

        :param uid: str, uid of user
        :param gid: str, name of group
        :returns:  resquester response
        """
        url = "{uid}/groups".format(uid=uid)
        msg = {'groupid': gid}
        return self.requester.post(url, data=msg)

    def remove_from_group(self, uid, gid):
        """
        Remove the specified user from the specified group

        :param uid: str, uid of user
        :param gid: str, name of group
        :returns:  resquester response
        """
        url = "{uid}/groups".format(uid=uid)
        msg = {'groupid': gid}
        return self.requester.delete(url, data=msg)

    def create_subadmin(self, uid, gid):
        """
        Make a user the subadmin of a group

        :param uid: str, uid of user
        :param gid: str, name of group
        :returns:  resquester response
        """
        url = "{uid}/subadmins".format(uid=uid)
        msg = {'groupid': gid}
        return self.requester.post(url, data=msg)

    def remove_subadmin(self, uid, gid):
        """
        Remove the subadmin rights for the user specified from the group specified

        :param uid: str, uid of user
        :param gid: str, name of group
        :returns:  resquester response
        """
        url = "{uid}/subadmins".format(uid=uid)
        msg = {'groupid': gid}
        return self.requester.delete(url, data=msg)

    def get_subadmin_groups(self, uid):
        """
        Get the groups in which the user is a subadmin

        :param uid: str, uid of user
        :returns:  resquester response
        """
        url = "{uid}/subadmins".format(uid=uid)
        return self.requester.get(url)

    def resend_welcome_mail(self, uid):
        """
        Trigger the welcome email for this user again

        :param uid: str, uid of user
        :returns:  resquester response
        """
        url = "{uid}/welcome".format(uid=uid)
        return self.requester.post(url)

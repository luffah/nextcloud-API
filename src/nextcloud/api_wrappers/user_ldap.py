# -*- coding: utf-8 -*-
"""
User LDAP wrapper
See https://docs.nextcloud.com/server/14/admin_manual/configuration_user/user_auth_ldap_api.html
    https://doc.owncloud.com/server/10.7/admin_manual/configuration/server/occ_commands/app_commands/ldap_integration_commands.html
"""
import re
from nextcloud import base


class UserLDAP(base.OCSv2ApiWrapper):
    """ User LDAP wrapper """
    API_URL = "/ocs/v2.php/apps/user_ldap/api/v1/config"

    CONFIG_KEYS = [
        "ldapHost",
        "ldapPort",
        "ldapBackupHost",
        "ldapBackupPort",
        "ldapBase",
        "ldapBaseUsers",
        "ldapBaseGroups",
        "ldapAgentName",
        "ldapAgentPassword",
        "ldapTLS",
        "turnOffCertCheck",
        "ldapUserDisplayName",
        "ldapGidNumber",
        "ldapUserFilterObjectclass",
        "ldapUserFilterGroups",
        "ldapUserFilter",
        "ldapUserFilterMode",
        "ldapGroupFilter",
        "ldapGroupFilterMode",
        "ldapGroupFilterObjectclass",
        "ldapGroupFilterGroups",
        "ldapGroupMemberAssocAttr",
        "ldapGroupDisplayName",
        "ldapLoginFilter",
        "ldapLoginFilterMode",
        "ldapLoginFilterEmail",
        "ldapLoginFilterUsername",
        "ldapLoginFilterAttributes",
        "ldapQuotaAttribute",
        "ldapQuotaDefault",
        "ldapEmailAttribute",
        "ldapCacheTTL",
        "ldapUuidUserAttribute",
        "ldapUuidGroupAttribute",
        "ldapOverrideMainServer",
        "ldapConfigurationActive",
        "ldapAttributesForUserSearch",
        "ldapAttributesForGroupSearch",
        "ldapExperiencedAdmin",
        "homeFolderNamingRule",
        "hasMemberOfFilterSupport",
        "useMemberOfToDetectMembership",
        "ldapExpertUsernameAttr",
        "ldapExpertUUIDUserAttr",
        "ldapExpertUUIDGroupAttr",
        "lastJpegPhotoLookup",
        "ldapNestedGroups",
        "ldapPagingSize",
        "turnOnPasswordChange",
        "ldapDynamicGroupMemberURL",
        "ldapDefaultPPolicyDN",
    ]

    def create_ldap_config(self):
        """ Create a new and empty LDAP configuration """
        return self.requester.post()

    def get_ldap_config_id(self, idx=1):
        """
        The LDAP config ID is a string.
        Given the number of the config file, return the corresponding string ID
        if the configuration exists.

        :param idx: The index of the configuration.
                 If a single configuration exists on the server from the beginning,
                 it is going to have index of 1.

        :returns:  Configuration string or None
        """
        config_id = 's%02d' % idx
        config = self.get_ldap_config(config_id)
        if config.is_ok:
            return config_id
        return None

    def get_ldap_lowest_existing_config_id(self, lower_bound=1, upper_bound=10):
        """
        Given (inclusive) lower and upper bounds, try to guess an existing LDAP config ID
        that corresponds to an index within those bounds.

        :param lower_bound: The lowest index of the configuration possible.
        :param upper_bound: The greatest index of the configuration possible.

        :returns: Configuration string or None
        """
        for idx in range(lower_bound, upper_bound + 1):
            config_id = self.get_ldap_config_id(idx)
            if config_id:
                return config_id

    def get_ldap_config(self, config_id, show_password=None):
        """
        Get all keys and values of the specified LDAP configuration

        :param config_id (str): User LDAP config id
        :param show_password (int): 0 or 1 whether to return the password in clear text (default 0)

        :returns: requester response
        """
        params = dict(showPassword=show_password)
        return self.requester.get(config_id, params=params)

    def edit_ldap_config(self, config_id, data):
        """
        Update a configuration with the provided values

        You can find list of all config keys in get_ldap_config method response or in
        Nextcloud docs

        :param config_id (str): User LDAP config id
        :param data (dict): config values to update

        :returns: requester response
        """
        prepared_data = {'configData[{}]'.format(key): value for key, value in data.items()}
        return self.requester.put(config_id, data=prepared_data)

    def ldap_cache_flush(self, config_id):
        """
        Flush the cache, so the fresh LDAP DB data is used.

        Implementation detail:
        This is performed by a fake update of LDAP cache TTL
        as indicated by

        :param config_id (str): User LDAP config id
        """
        cache_val = self.get_ldap_cache_ttl(config_id)
        self.set_ldap_cache_ttl(config_id, cache_val)

    def delete_ldap_config(self, config_id):
        """
        Delete a given LDAP configuration

        :param config_id (str): User LDAP config id

        :returns: requester response
        """
        return self.requester.delete(config_id)


for ldap_key in UserLDAP.CONFIG_KEYS:
    key_name = re.sub('ldap', '', ldap_key)
    key_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', key_name).lower()

    # create and add getter method
    getter_name = "get_ldap_{}".format(key_name)

    def getter_method(param):
        def getter(self, config_id):
            res = self.get_ldap_config(config_id)
            data = res.data
            return data[param]
        getter.__name__ = getter_name
        return getter

    setattr(UserLDAP, getter_name, getter_method(ldap_key))

    # create and add setter method
    setter_name = "set_ldap_{}".format(key_name)

    def setter_method(param):
        def setter(self, config_id, value):
            res = self.edit_ldap_config(config_id, data={param: value})
            return res
        setter.__name__ = setter_name
        return setter

    setattr(UserLDAP, setter_name, setter_method(ldap_key))

import re
try:
    from unittest.mock import patch
except ImportError:
    import unittest
    from mock import patch

from .base import BaseTestCase

from nextcloud.api_wrappers.user_ldap import UserLDAP


class TestUserLDAP(BaseTestCase):

    def setUp(self):
        super(TestUserLDAP, self).setUp()
        self.nxc.enable_app('user_ldap')

    def test_crud_ldap_config(self):
        res = self.nxc.create_ldap_config()
        assert res.is_ok
        config_id = res.data['configID']

        # We assume that the ID has format s{number}
        config_number = int(config_id[1:])
        inferred_config_id = self.nxc.get_ldap_lowest_existing_config_id(
                config_number - 2, config_number + 2)
        res = self.nxc.get_ldap_config(inferred_config_id)
        assert res.is_ok

        self.nxc.ldap_cache_flush(config_id)

        # test get config by id
        res = self.nxc.get_ldap_config(config_id)
        assert res.is_ok
        config_data = res.data

        # test edit config
        param_to_change = "ldapPagingSize"
        old_param_value = config_data[param_to_change]
        new_param_value = 777
        assert old_param_value != new_param_value
        res = self.nxc.edit_ldap_config(config_id, data={param_to_change: new_param_value})
        assert res.is_ok
        new_config_data = self.nxc.get_ldap_config(config_id).data
        assert str(new_config_data[param_to_change]) == str(new_param_value)

        # test showPassword param
        ldap_password_param = "ldapAgentPassword"
        ldap_password_value = "test_password"
        self.nxc.edit_ldap_config(config_id, {ldap_password_param: ldap_password_value})
        config_data_without_password = self.nxc.get_ldap_config(config_id).data
        assert config_data_without_password[ldap_password_param] == "***"
        config_data_with_password = self.nxc.get_ldap_config(config_id, show_password=1).data
        assert config_data_with_password[ldap_password_param] == ldap_password_value

        # test delete config
        res = self.nxc.delete_ldap_config(config_id)
        assert res.is_ok
        res = self.nxc.get_ldap_config(config_id)
        assert res.status_code == self.NOT_FOUND_CODE

    def test_ldap_setters_getters(self):
        res = self.nxc.create_ldap_config()
        assert res.is_ok
        assert res.status_code == 200
        config_id = res.data['configID']

        for ldap_key in UserLDAP.CONFIG_KEYS:
            key_name = re.sub('ldap', '', ldap_key)
            key_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', key_name).lower()

            getter_name = "get_ldap_{}".format(key_name)
            setter_name = "set_ldap_{}".format(key_name)
            # test if method exist
            assert hasattr(self.nxc, setter_name)
            assert hasattr(self.nxc, getter_name)

            # test getter
            getter_value = getattr(self.nxc, getter_name)(config_id)
            config_value = self.nxc.get_ldap_config(config_id).data[ldap_key]
            assert getter_value == config_value

            # test setter
            value = 1
            with patch.object(UserLDAP, 'edit_ldap_config', return_value=1) as mock_method:
                setter_method = getattr(self.nxc, setter_name)
                setter_method(config_id, value)
                mock_method.assert_called_with(config_id, data={ldap_key: value})

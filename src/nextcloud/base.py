# -*- coding: utf-8 -*-
"""
Define what is an api wrapper
"""
import six
from nextcloud.requester import Requester, OCSRequester, WebDAVRequester
from nextcloud.codes import ProvisioningCode, OCSCode, WebDAVCode

API_WRAPPER_CLASSES = []


class MetaWrapper(type):
    def __new__(meta, name, bases, attrs):
        cls = type.__new__(meta, name, bases, attrs)
        if (cls.API_URL != NotImplementedError and cls.VERIFIED):
            API_WRAPPER_CLASSES.append(cls)
        return cls


class BaseApiWrapper(object, six.with_metaclass(MetaWrapper)):
    """
    Define an API wrapper

    Example of an abstract API wrapper.
    >>> class ApiWrapper(BaseApiWrapper):
    >>>    REQUESTER = WebDAVRequester
    >>>    SUCCESS_CODE = 100


    If API_URL is provided (and if attribute ''VERIFIED = False'' is not in the new
    class),then public methods of the class are added to NextCloud object.
    Example of a concerete API wrapper.
    >>> class Info(ApiWrapper):
    >>>    API_URL = 'remote.php/info'
    >>>
    >>>    def get_info(self):
    >>>        return self.requester.get()

    """
    API_URL = NotImplementedError
    VERIFIED = True
    JSON_ABLE = True
    REQUIRE_CLIENT = False
    REQUIRE_USER = False
    REQUESTER = Requester

    def __init__(self, session, json_output=None, client=None, user=None):
        self.json_output = json_output
        self.client = client
        self.user = user
        self.requester = self.REQUESTER(session, json_output=json_output)

        for attr_name in ['API_URL', 'SUCCESS_CODE', 'METHODS_SUCCESS_CODES']:
            setattr(self.requester, attr_name, getattr(self, attr_name, None))

    def _arguments_get(self, varnames, vals):
        """
        allows to automatically fetch values of varnames
        using generic values computing '_default_get_VARNAME'

        Example
        >>> def get_file_id(self, **kwargs):
        >>>     file_id, = self._arguments_get(['file_id'], locals())
        >>>
        >>> def _default_get_file_id(self, vals):
        >>>     return self.get_file_id_from_name(vals.get('name', None))
        >>>
        >>> nxc.get_file_id(name='foo.bar')
        """
        if 'kwargs' in vals:
            vals.update(vals['kwargs'])
        ret = []
        for varname in varnames:
            val = vals.get(varname, None)
            if val is None:
                getter_func_name = '_default_get_%s' % varname
                if hasattr(self, getter_func_name):
                    val = getattr(self, getter_func_name)(vals)
            ret.append(val)

        return ret




class ProvisioningApiWrapper(BaseApiWrapper):
    """ Define "Provisioning API" wrapper classes """
    REQUESTER = OCSRequester
    SUCCESS_CODE = ProvisioningCode.SUCCESS


class OCSv1ApiWrapper(BaseApiWrapper):
    """ Define OCS wrapper classes """
    REQUESTER = OCSRequester
    SUCCESS_CODE = OCSCode.SUCCESS_V1


class OCSv2ApiWrapper(BaseApiWrapper):
    """ Define OCS wrapper classes """
    REQUESTER = OCSRequester
    SUCCESS_CODE = OCSCode.SUCCESS_V2


class WebDAVApiWrapper(BaseApiWrapper):
    """ Define WebDav wrapper classes """
    REQUESTER = WebDAVRequester

    SUCCESS_CODE = {
        'PROPFIND': [WebDAVCode.MULTISTATUS],
        'PROPPATCH': [WebDAVCode.MULTISTATUS],
        'REPORT': [WebDAVCode.MULTISTATUS],
        'MKCOL': [WebDAVCode.CREATED],
        'COPY': [WebDAVCode.CREATED, WebDAVCode.NO_CONTENT],
        'MOVE': [WebDAVCode.CREATED, WebDAVCode.NO_CONTENT],
        'PUT': [WebDAVCode.CREATED],
        'POST': [WebDAVCode.CREATED],
        'DELETE': [WebDAVCode.NO_CONTENT]
    }

# -*- coding: utf-8 -*-
"""
Define what is an api wrapper
"""
import six
from nextcloud.requester import Requester, OCSRequester, WebDAVRequester
from nextcloud.codes import ProvisioningCode, OCSCode, WebDAVCode

API_WRAPPER_CLASSES = []


class MetaWrapper(type):
    """ Meta class to register wrappers """
    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        if (new_cls.API_URL != NotImplementedError and new_cls.VERIFIED):
            API_WRAPPER_CLASSES.append(new_cls)
        return new_cls


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
    REQUESTER = Requester

    def __init__(self, client=None):
        self.client = client
        self.requester = self.REQUESTER(self)

        for attr_name in ['API_URL', 'SUCCESS_CODE', 'METHODS_SUCCESS_CODES']:
            setattr(self.requester, attr_name, getattr(self, attr_name, None))

    @property
    def json_output(self):
        return self.JSON_ABLE and self.client.json_output

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

        :param varmames: list of wanted python var names
        :param vals: a dict object containing already set variables
        :returns:  list of wanted values
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

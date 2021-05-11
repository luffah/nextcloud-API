# -*- coding: utf-8 -*-
"""
Define what is an api wrapper
"""
import six
from nextcloud.requester import Requester, OCSRequester, WebDAVRequester
from nextcloud.codes import ProvisioningCode, OCSCode, WebDAVCode

API_WRAPPER_CLASSES = []


def get_wrapper_methods(obj):
    wrapper_methods = []
    for attr_name in dir(obj):
        if not (
                attr_name.isupper() or
                attr_name.startswith('_')
        ):
            attr_val = getattr(obj, attr_name)
            if callable(attr_val):
                wrapper_methods.append((attr_name, attr_val))
    return wrapper_methods


class MetaWrapper(type):
    """ Meta class to register wrappers """
    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        if (new_cls.API_URL != NotImplementedError and new_cls.VERIFIED):
            API_WRAPPER_CLASSES.append(new_cls)
        for k, method in get_wrapper_methods(new_cls):
            obj = getattr(method, '__associated_object', False)
            getter_method_name = getattr(method, '__getter_method_name', False)
            uniq = getattr(method, '__getter_method_get_first', False)
            skip_first = getattr(method, '__getter_method_skip_first', False)
            obj_kwargs = getattr(method, '__associated_object_kwargs', {})
            if not obj:
                continue

            orig_method = method

            def _mod_method(self, json_output=True, *args, **kwargs):
                resp = orig_method(self, *args, **kwargs)
                if json_output is None:
                    json_output = self.json_output
                return obj.from_response(resp, wrapper=self,
                                         json_output=json_output,
                                         **obj_kwargs)

            setattr(_mod_method, '__doc__',
                    method.__doc__ +
                    "\n:returns: requester response with list<%s> in data" %
                    obj.__name__
                    )
            setattr(new_cls, k, _mod_method)

            if getter_method_name:
                def _getter_method(self, *args, **kwargs):
                    ret = _mod_method(self, json_output=False, *args, **kwargs)
                    if ret.data:
                        ret = ret.data
                        if skip_first and ret[0].href.endswith('/'):
                            ret = ret[1:]
                    else:
                        ret = []
                    return ret

                if uniq:
                    def _getter_method_uniq(self, *args, **kwargs):
                        ret = _getter_method(self, *args, **kwargs)
                        return ret[0] if ret else None
                    setattr(_getter_method_uniq, '__doc__',
                            "(get uniq object or None)\n" + method.__doc__ +
                            "\n:returns: a %s or None" % obj.__name__)
                    setattr(new_cls, getter_method_name, _getter_method_uniq)
                else:
                    setattr(_getter_method, '__doc__',
                            "(get object list)\n" + method.__doc__ +
                            "\n:returns: a list<%s>" % obj.__name__)
                    setattr(new_cls, getter_method_name, _getter_method)

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

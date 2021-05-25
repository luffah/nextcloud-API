# -*- coding: utf-8 -*-
"""
Define requests responses (automatically check if the request is OK)
"""
try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

from .common import parse_xml as ParseXML


# pylint: disable=useless-object-inheritance, too-many-instance-attributes
class BaseResponse(object):
    """
    Base Response that take HTTP reponse and take the following attrs
    - raw         : the raw response
    - data        : (optionnal) the value of response data

    The following attribute are guessed / recomputed
    - data        : the associated data / dictionnary-like data or binary
    - status_code : the HTTP code
    - json_data   : the data in a json dict
    - content_data: the data in raw.content as a unicode string
    - is_ok       : True if the request is succesfully achieved
    """

    def __init__(self, response, data=None, success_code=None):
        self.raw = response
        self.data = data

        self._status_code = None
        self._json_data = None
        self._content_data = None
        self._raw_content_data = None
        self._is_ok = None

        self.success_code = success_code

        self._complete_data()

    @property
    def json_data(self):
        """ Return JSON version of the response """
        if not self._json_data:
            self._json_data = self.get_json_data()
        return self._json_data

    @property
    def content_data(self):
        """ Return (unicode string) content of the response """
        if not self._content_data:
            self._content_data = self.get_content_data()
        return self._content_data

    @property
    def raw_content_data(self):
        """ Return raw content of the response """
        if not self._raw_content_data:
            self._raw_content_data = self.get_raw_content_data()
        return self._raw_content_data

    @property
    def status_code(self):
        """ Return (unicode string) content of the response """
        if self._status_code is None:
            self._status_code = self.raw.status_code
        return int(self._status_code or -1)

    @property
    def is_ok(self):
        """ Return true if status_code match success code """
        if self._is_ok is None:
            success_code = self.success_code
            if isinstance(success_code, dict):
                method = self.raw.request.method
                success_codes = success_code.get(method, [])
            else:
                success_codes = (
                    success_code if isinstance(success_code, list) else
                    [success_code]
                )

            self._is_ok = self.status_code in success_codes
        return self._is_ok

    def get_json_data(self):
        """ Return JSON version of the response """
        data = self.get_content_data()
        if data.startswith("<?xml"):
            data = ParseXML.etree_to_dict(
                ParseXML.fromstring(data)
            )
        else:
            try:
                data = self.raw.json()
            except JSONDecodeError:
                data = {'message': 'Unable to parse JSON response'}
        return data

    def get_content_data(self):
        """ Return (unicode string) content of the response """
        return self.raw.content.decode('UTF-8')

    def get_raw_content_data(self):
        """ Return (binary) content of the response """
        return self.raw.content

    def _complete_data(self):
        if self.data is None:
            self.data = self.content_data

    def __repr__(self):
        is_ok_str = "OK" if self.is_ok else "Failed"
        return "<{}: Status: {}>".format(self.__class__.__name__, is_ok_str)


class OCSResponse(BaseResponse):
    """
    Response class for OCS api methods
    Add some computed attributes:
    - meta      : ocs json metadata
    - full_data : json data of the ocs response
    """

    def _complete_data(self):
        meta = None
        data = None

        full_data = self.get_json_data()

        if full_data:
            if 'ocs' in full_data:
                ocs_data = full_data['ocs']
                meta = ocs_data['meta']
                self._status_code = meta['statuscode']
                data = ocs_data['data']
            else:
                data = full_data
                meta = data
                self._status_code = -1

        if self.data is None:
            self.data = data

        self._json_data = data

        self.full_data = full_data
        self.meta = meta

class ProvisioningApiResponse(OCSResponse):
    """ Response class for Provisioning api methods """


class WebDAVResponse(BaseResponse):
    """ Response class for WebDAV api methods """

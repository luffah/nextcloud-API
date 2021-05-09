# -*- coding: utf-8 -*-
"""
Define requests responses (automatically check if the request is OK)
"""
try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


class BaseResponse(object):
    """
    Base Response that take HTTP reponse and take the following attrs
    - raw         : the raw response
    - status_code : the HTTP code
    - data        : the asked data (json or xml value)
    - is_ok       : True if the request is succesfully achieved
    """

    def __init__(self, response, data=None, json_output=True,
                 status_code=None, success_code=None, **kwargs):
        self.raw = response
        self.data = data if data is not None else (
            response.json() if json_output else response.content.decode('UTF-8')
        )
        self.status_code = status_code or response.status_code
        for k in kwargs:
            setattr(self, k, kwargs[k])
        self._compute_is_ok(success_code)

    def _compute_is_ok(self, success_code):
        if isinstance(success_code, dict):
            method = self.raw.request.method
            success_codes = success_code.get(method, [])
        else:
            success_codes = (
                success_code if isinstance(success_code, list) else
                [success_code]
            )

        self.is_ok = self.status_code in success_codes

    def __repr__(self):
        is_ok_str = "OK" if self.is_ok else "Failed"
        return "<{}: Status: {}>".format(self.__class__.__name__, is_ok_str)


class OCSResponse(BaseResponse):
    """
    Response class for OCS api methods
    Add some attributes:
    - meta      : ocs json metadata
    - full_data : json data of the ocs response
    """

    def __init__(self, response, json_output=True, success_code=None):
        data = None
        full_data = None
        meta = None
        status_code = None
        if (success_code or json_output):
            try:
                full_data = response.json()
                if 'ocs' in full_data:
                    ocs_data = full_data['ocs']
                    meta = ocs_data['meta']
                    status_code = meta['statuscode']
                    if json_output:
                        data = ocs_data['data']
                else:
                    data = full_data
                    meta = data
                    status_code = -1
            except JSONDecodeError:
                data = {'message': 'Unable to parse JSON response'}
                meta = data
                status_code = -1

        super(OCSResponse, self).__init__(response, data=data,
                                          json_output=json_output,
                                          full_data=full_data,
                                          status_code=status_code,
                                          meta=meta,
                                          success_code=success_code)


class WebDAVResponse(BaseResponse):
    """ Response class for WebDAV api methods """

    def __init__(self, response, data=None, success_code=None, json_output=False):
        super(WebDAVResponse, self).__init__(response, data=data,
                                             json_output=json_output,
                                             success_code=success_code)

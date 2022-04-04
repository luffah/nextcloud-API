#pylint: disable=unnecessary-utf8-coding-comment
# -*- coding: utf-8 -*-
"""
Define requesters
"""
from . import response
from .compat import encode_string


# from six.moves.urllib import parse
def _prepare_url(string):
    return encode_string(string)
#     if six.PY2 and isinstance(string, unicode):  # noqa: F821
#         return parse.urlparse(string).path
#     return s


# pylint: disable=useless-object-inheritance
class Requester(object):
    """ Base requester """

    headers = {}

    def __init__(self, wrapper):
        self.query_components = []
        self.wrapper = wrapper

    @staticmethod
    def _setup_headers(headers):
        """ Add information in headers (default nothing) """

    @classmethod
    def get_headers(cls, key, headers=None):
        """ Add information in headers (default nothing) """
        h_dict = cls.headers.get(key, {})
        if not h_dict:
            if key[0] == 'p':  # put or post
                h_dict['Content-Type'] = (
                    'application/json' if '/json' in key else
                    'application/x-www-form-urlencoded'
                )
            cls._setup_headers(h_dict)
            cls.headers[key] = h_dict
        if headers:
            h_dict = h_dict.copy()
            h_dict.update(headers)
        return h_dict

    @property
    def response_type(self):
        """ Response type defaulted to BaseResponse"""
        return response.BaseResponse

    @property
    def client(self):
        """ The NextCloud client associated to the requester """
        return self.wrapper.client

    @property
    def session(self):
        """ The NextCloud session associated to the requester """
        return self.wrapper.client.session

    @property
    def api_url(self):
        """ The sub url associated to the requester """
        #FIXME may change according to server url ?
        return self.wrapper.API_URL

    @property
    def json_able(self):
        """ Define response type of the requests """
        return self.wrapper.JSON_ABLE

    @property
    def success_code(self):
        """ The success code (<int> or <dict method_name: int>)"""
        return self.wrapper.SUCCESS_CODE

    def rtn(self, resp, raw_content=None):
        """ Build the response from requests response (see response_type) """
        # print(resp)
        # print(resp.content)
        return self.response_type(
            response=resp, raw_content=raw_content,
            success_code=self.success_code
        )

    def get_full_url(self, additional_url=""):
        """
        Build full url for request to NextCloud api

        Construct url from base_url, API_URL and additional_url (if given),
        add format=json param if json_able

        :param additional_url: str
            add to url after api_url
        :return: str
        """
        if isinstance(additional_url, int):
            additional_url = str(additional_url)

        if additional_url:
            additional_url = _prepare_url(additional_url)
            if not additional_url.startswith("/"):
                additional_url = "/{}".format(additional_url)
        if self.json_able:
            self.query_components.append("format=json")
        ret = "{base_url}{api_url}{additional_url}".format(base_url=self.session.url,
                                                           api_url=self.api_url,
                                                           additional_url=additional_url)
        if self.json_able:
            ret += "?format=json"

        return ret

    # pylint: disable=too-many-arguments

    def request(self, method, url, headers=None, params=None,
                data=None, raw_content=False):
        """
        Apply the request using 'requests' lib

        :param method (str):   the method name / content type (e.g. 'post/json')
        :param url (str):      the relative url
        :param headers:        custom header
        :param params:         requests parameters
        :param data:           data to push with the request
        :param raw_content:    use requests.Response content instead of default one

        :returns: BaseResponse inherited (see response_type property)
        """
        headers = self.get_headers(method, headers)
        if '/' in method:
            method = method.split('/')[0]
        url = self.get_full_url(url)
        res = self.session.request(method, url, headers=headers,
                                   params=params, data=data)
        return self.rtn(res, raw_content=raw_content)

    def get(self, url="", **kwargs):
        " get request "
        return self.request('get', url, **kwargs)

    def post(self, url="", data=None, **kwargs):
        " post request "
        return self.request('post', url, data=data, **kwargs)

    def post_json(self, url="", data=None, **kwargs):
        " post request posting json datas "
        return self.request('post/json', url, data=data, **kwargs)

    def put(self, url="", data=None, **kwargs):
        " put request "
        return self.request('put', url, data=data, **kwargs)

    def put_with_timestamp(self, url="", data=None, timestamp=None, headers=None, **kwargs):
        " put request with additional timestamp "
        headers = headers or {}
        if isinstance(timestamp, (float, int)):
            headers['X-OC-MTIME'] = '%.0f' % timestamp
        return self.request('put', url, data=data, headers=headers, **kwargs)

    def delete(self, url="", **kwargs):
        " delete request "
        return self.request('delete', url, **kwargs)


class OCSRequester(Requester):
    """ Requester for OCS API """

    @staticmethod
    def _setup_headers(headers):
        """ Add OCS specific in header """
        headers["OCS-APIRequest"] = "true"

    # @classmethod
    # def get_headers(cls, key, headers=None):
    #     return super(OCSRequester, cls).get_headers(key + '/ocs', headers=headers)

    @property
    def response_type(self):
        """ Response type is OCSResponse """
        return response.OCSResponse

class ProvisioningApiRequester(OCSRequester):
    """ Requester for Provisionning API """

    @property
    def response_type(self):
        """ Response type is OCSResponse """
        return response.ProvisioningApiResponse



class WebDAVRequester(Requester):
    """ Requester for WebDAV API """

    # @classmethod
    # def get_headers(cls, key, headers=None):
    #     return super(WebDAVRequester, cls).get_headers(key + '/webdav', headers=headers)

    @property
    def response_type(self):
        """ Response type is WEBDAVResponse """
        return response.WebDAVResponse

    def propfind(self, url="", **kwargs):
        " propfind request "
        return self.request('propfind', url, **kwargs)

    def proppatch(self, url="", **kwargs):
        " proppatch request "
        return self.request('proppatch', url, **kwargs)

    def report(self, url="", **kwargs):
        " report request "
        return self.request('report', url, **kwargs)

    def download(self, url="", params=None):
        " download request "
        return self.request('get', url, params=params, raw_content=True)

    def make_collection(self, url=""):
        " mkcol request (make dir) "
        return self.request("mkcol", url)

    def move(self, url, destination, overwrite=False):
        " move request (move file) "
        destination_url = self.get_full_url(destination)
        headers = {"Destination": destination_url.encode("utf-8"),
                   "Overwrite": "T" if overwrite else "F"}
        return self.request("move", url=url, headers=headers)

    def copy(self, url, destination, overwrite=False):
        " copy request (copy file) "
        destination_url = self.get_full_url(destination)
        headers = {"Destination": destination_url.encode("utf-8"),
                   "Overwrite": "T" if overwrite else "F"}
        return self.request("copy", url=url, headers=headers)

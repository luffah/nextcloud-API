# -*- coding: utf-8 -*-
from .response import WebDAVResponse, OCSResponse
from .compat import encode_string
from .session import catch_connection_error


def _prepare_url(s):
    return encode_string(s)


class Requester(object):

    def __init__(self, session, json_output=None, url=None,
                 success_code=None):
        self.query_components = []
        self.h_get = {'OCS-APIRequest': 'true'}
        self.h_post = {'OCS-APIRequest': 'true',
                       'Content-Type': 'application/x-www-form-urlencoded'}
        self.session = session
        self.json_output = None
        self.API_URL = None
        self.SUCCESS_CODE = None

    def rtn(self, resp):
        if self.json_output:
            return resp.json()
        else:
            return resp.content.decode('UTF-8')

    @catch_connection_error
    def get(self, url='', params=None, headers=None):
        url = self.get_full_url(url)
        res = self.session.request('get', url, headers=(headers or self.h_get),
                                   params=params)
        return self.rtn(res)

    @catch_connection_error
    def post(self, url='', data=None, headers=None):
        url = self.get_full_url(url)
        res = self.session.request(
            'post', url, data=data, headers=(headers or self.h_post))
        return self.rtn(res)

    @catch_connection_error
    def put_with_timestamp(self, url='', data=None, timestamp=None, headers=None):
        h_post = headers or self.h_post
        if isinstance(timestamp, (float, int)):
            h_post['X-OC-MTIME'] = '%.0f' % timestamp
        url = self.get_full_url(url)
        res = self.session.request('put', url, data=data, headers=h_post)
        return self.rtn(res)

    @catch_connection_error
    def put(self, url='', data=None, headers=None):
        url = self.get_full_url(url)
        res = self.session.request(
            'put', url, data=data, headers=(headers or self.h_post))
        return self.rtn(res)

    @catch_connection_error
    def delete(self, url='', data=None, headers=None):
        url = self.get_full_url(url)
        res = self.session.request(
            'delete', url, data=data, headers=(headers or self.h_post))
        return self.rtn(res)

    def get_full_url(self, additional_url=''):
        """
        Build full url for request to NextCloud api

        Construct url from base_url, API_URL and additional_url (if given),
        add format=json param if self.json

        :param additional_url: str
            add to url after api_url
        :return: str
        """
        if isinstance(additional_url, int):
            additional_url = str(additional_url)
        else:
            if additional_url:
                additional_url = _prepare_url(additional_url)
                if not additional_url.startswith('/'):
                    additional_url = '/{}'.format(additional_url)
            if self.json_output:
                self.query_components.append('format=json')
            ret = '{base_url}{api_url}{additional_url}'.format(base_url=(self.session.url),
                                                               api_url=(
                                                                   self.API_URL),
                                                               additional_url=additional_url)
            if self.json_output:
                ret += '?format=json'
        return ret


class OCSRequester(Requester):
    __doc__ = ' Requester for OCS API '

    def rtn(self, resp):
        return OCSResponse(response=resp, json_output=(self.json_output),
                           success_code=(self.SUCCESS_CODE))


class WebDAVRequester(Requester):
    __doc__ = ' Requester for WebDAV API '

    def __init__(self, *args, **kwargs):
        (super(WebDAVRequester, self).__init__)(*args, **kwargs)

    def rtn(self, resp, data=None):
        return WebDAVResponse(response=resp, data=data,
                              success_code=self.SUCCESS_CODE)

    @catch_connection_error
    def propfind(self, additional_url='', headers=None, data=None):
        url = self.get_full_url(additional_url=additional_url)
        res = self.session.request('PROPFIND', url, headers=headers, data=data)
        return self.rtn(res)

    @catch_connection_error
    def proppatch(self, additional_url='', data=None):
        url = self.get_full_url(additional_url=additional_url)
        res = self.session.request('PROPPATCH', url, data=data)
        return self.rtn(resp=res)

    @catch_connection_error
    def report(self, additional_url='', data=None):
        url = self.get_full_url(additional_url=additional_url)
        res = self.session.request('REPORT', url, data=data)
        return self.rtn(resp=res)

    @catch_connection_error
    def download(self, url='', params=None):
        url = self.get_full_url(url)
        res = self.session.request(
            'get', url, headers=(self.h_get), params=params)
        return self.rtn(resp=res, data=(res.content))

    @catch_connection_error
    def make_collection(self, additional_url=''):
        url = self.get_full_url(additional_url=additional_url)
        res = self.session.request('MKCOL', url=url)
        return self.rtn(resp=res)

    @catch_connection_error
    def move(self, url, destination, overwrite=False):
        url = self.get_full_url(additional_url=url)
        destination_url = self.get_full_url(additional_url=destination)
        headers = {'Destination': destination_url.encode('utf-8'),
                   'Overwrite': 'T' if overwrite else 'F'}
        res = self.session.request('MOVE', url=url, headers=headers)
        return self.rtn(resp=res)

    @catch_connection_error
    def copy(self, url, destination, overwrite=False):
        url = self.get_full_url(additional_url=url)
        destination_url = self.get_full_url(additional_url=destination)
        headers = {'Destination': destination_url.encode('utf-8'),
                   'Overwrite': 'T' if overwrite else 'F'}
        res = self.session.request('COPY', url=url, headers=headers)
        return self.rtn(resp=res)

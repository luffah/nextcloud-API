# -*- coding: utf-8 -*-
""" Exceptions """


class NextCloudError(Exception):
    """ An error occurred """

    def __init__(self, msg='', url='', obj=None):
        self.message = msg
        self.url = url
        self.obj = obj
        Exception.__init__(self, msg, url, obj)


class NextCloudConnectionError(NextCloudError):
    """ A connection error occurred """


class NextCloudLoginError(NextCloudError):
    """ A login error occurred """




# -*- coding: utf-8 -*-
"""
Tools for python2/3 unicode compatibility
"""
import six
import time


def encode_requests_password(word):
    """
    Convert the string to bytes (readable by the server)

    :param word: input string
    :returns:    bytes with appropriate encoding
    """
    if isinstance(word, bytes):
        return word

    ret = word
    if six.PY2:
        if isinstance(word, six.text_type):
            # trick to work with tricks in requests lib
            ret = word.encode('utf-8').decode('latin-1')
    else:
        try:
            ret = bytes(word, 'ascii')
        except UnicodeEncodeError:
            ret = bytes(word, 'utf-8')
    return ret


def encode_string(string):
    """Encodes a unicode instance to utf-8. If a str is passed it will
    simply be returned

    :param string: str or unicode to encode
    :returns     : encoded output as str
    """
    if six.PY2:
        if isinstance(string, six.text_type):
            return string.encode('utf-8')
    return string


def datetime_to_timestamp(_time):
    """
    :returns: int(<datetime>.timestamp())
    """
    if six.PY2:
        return int(
            time.mktime(_time.timetuple()) + _time.microsecond/1000000.0
        )
    return int(
        _time.timestamp()
    )

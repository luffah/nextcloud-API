# -*- coding: utf-8 -*-
"""
Extra tools for value parsing
"""
from datetime import datetime
import os
from nextcloud.compat import timestamp_from_datetime

DATETIME_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'

def datetime_to_expire_date(date):
    return date.strftime("%Y-%m-%d")

def datetime_from_string(rfc1123_date):
    """
    Parse date string to datetime (UTC)
    :param rfc1123_date (str): rfc1123-date (defined in RFC2616)
    :returns: datetime or None
    """
    _time = None
    try:
        _tz = os.environ.get('TZ', '')
        os.environ['TZ'] = 'UTC'
        _time = datetime.strptime(rfc1123_date, DATETIME_FORMAT)
        os.environ['TZ'] = _tz
    except ValueError:
        pass
    return _time


def timestamp_from_string(rfc1123_date=''):
    """
    literal date time string (use in DAV:getlastmodified) to Epoch time

    No longer, Only rfc1123-date productions are legal as values for DAV:getlastmodified
    However, the value may be broken or invalid.

    Args:
        rfc1123_date (str): rfc1123-date (defined in RFC2616)
    Return:
        int or None : Epoch time, if date string value is invalid return None
    """
    _time = datetime_from_string(rfc1123_date)
    return timestamp_from_datetime(_time) if _time else None

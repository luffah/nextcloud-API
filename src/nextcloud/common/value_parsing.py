# -*- coding: utf-8 -*-
"""
Extra tools for value parsing
"""
from datetime import datetime
from nextcloud.compat import datetime_to_timestamp


def timestamp_to_epoch_time(rfc1123_date=''):
    """
    literal date time string (use in DAV:getlastmodified) to Epoch time

    No longer, Only rfc1123-date productions are legal as values for DAV:getlastmodified
    However, the value may be broken or invalid.

    Args:
        rfc1123_date (str): rfc1123-date (defined in RFC2616)
    Return:
        int or None : Epoch time, if date string value is invalid return None
    """
    try:
        _time = datetime.strptime(
            rfc1123_date, '%a, %d %b %Y %H:%M:%S GMT')
    except ValueError:
        return
    else:
        return datetime_to_timestamp(_time)

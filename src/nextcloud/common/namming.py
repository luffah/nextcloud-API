# -*- coding: utf-8 -*-
"""
Define default namming of item properties
"""
import re

def py_to_json_name(name):
    ret = re.subn('([._])([a-z])', lambda m: m.group(2).upper(), name)
    if ret:
        return ret[0]
    return name

def py_to_xml_name(name):
    return name.replace('_', '-')

def xml_to_py_name(name):
    return name.replace('-', '_')


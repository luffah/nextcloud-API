# -*- coding: utf-8 -*-
"""
XML builder
"""
import xml.etree.ElementTree as ET
from ..api.properties import NAMESPACES_MAP


def _safe_xml_val(val):
    if isinstance(val, int):
        val = str(val)
    return val

SUPPORTED_FIELD_TYPES = list(NAMESPACES_MAP.keys())
XML_NAMESPACES_MAP = {'xmlns:' + k: v for k, v in NAMESPACES_MAP.items()}

def _to_fields_list(fields_hash):
    props_xml = []
    for field_type in fields_hash:
        if field_type not in SUPPORTED_FIELD_TYPES:
            pass
        else:
            for field in fields_hash[field_type]:
                props_xml.append('{}:{}'.format(field_type, field))

    return props_xml

def _to_field_vals_list(fields_hash):
    props_xml = {}
    for field_type in fields_hash:
        if field_type not in SUPPORTED_FIELD_TYPES:
            pass
        else:
            vals = fields_hash[field_type]
            for field in vals:
                props_xml['{}:{}'.format(field_type, field)] = _safe_xml_val(vals[field])

    return props_xml

def _tostring(root):
    return ET.tostring(root)

def build_propfind_datas(instr=None, filter_rules=None, fields=None):
    """
    Build XML datas for a PROPFIND querry.

    :param instr:        http instruction (default: PROPFIND)
    :param filter_rules: a dict containing filter rules separated by
                         namespace. e.g. {'oc': {'favorite': 1}}
    :param fields:       a dict containing fields separated by namespace
                         e.g. {'oc': ['id']}
    :returns:            xml data (string)
    """
    if not instr:
        instr = 'd:propfind'

    _namespaces = XML_NAMESPACES_MAP
    fields = fields or {}
    filter_rules = filter_rules or {}
    if fields or filter_rules:
        # restrict namespaces
        _namespaces = {}
        for k in XML_NAMESPACES_MAP:
            _k = k.split(':')[-1]
            if (
                    _k not in ['d', 'oc'] and
                    bool(fields.get(_k, [])) and
                    bool(filter_rules.get(_k, {}))
            ):
                continue
            _namespaces[k] = XML_NAMESPACES_MAP[k]

    root = ET.Element(instr, _namespaces)
    props = _to_fields_list(fields)
    if props:
        prop_group = ET.SubElement(root, 'd:prop')
        for prop in props:
            ET.SubElement(prop_group, prop)

    rules = _to_field_vals_list(filter_rules or {})
    if rules:
        rule_group = ET.SubElement(root, 'oc:filter-rules')
        for k in rules:
            rule = ET.SubElement(rule_group, k)
            val = rules[k]
            rule.text = _safe_xml_val(val)

    return _tostring(root)

def build_propupdate_datas(values):
    """
    Build XML datas for a PROPUPDATE querry.

    :param values:       a dict containing values separated by namespace
                         e.g. {'oc': {'favorite': 1}}
    :returns:            xml data (string)
    """
    root = ET.Element('d:propertyupdate', XML_NAMESPACES_MAP)
    vals = _to_field_vals_list(values)
    if vals:
        set_group = ET.SubElement(root, 'd:set')
        val_group = ET.SubElement(set_group, 'd:prop')
        for k in vals:
            val = ET.SubElement(val_group, k)
            val.text = vals[k]

    return _tostring(root)

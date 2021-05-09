# -*- coding: utf-8 -*-
"""
XML builder/parser
"""
import xml.etree.ElementTree as ET
from nextcloud.compat import encode_string
from nextcloud.common.properties import NAMESPACES_MAP


def _prepare_xml_parsing(string):
    return encode_string(string)

def _safe_xml_val(val):
    if isinstance(val, int):
        val = str(val)
    return val

class SimpleXml:
    """
    Static class to build and parse XML datas
    """
    namespaces_map = NAMESPACES_MAP
    supported_field_types = list(NAMESPACES_MAP.keys())
    xml_namespaces_map = {'xmlns:' + k: v for k, v in NAMESPACES_MAP.items()}

    @classmethod
    def _to_fields_list(cls, fields_hash):
        props_xml = []
        for field_type in fields_hash:
            if field_type not in cls.supported_field_types:
                pass
            else:
                for field in fields_hash[field_type]:
                    props_xml.append('{}:{}'.format(field_type, field))

        return props_xml

    @classmethod
    def _to_field_vals_list(cls, fields_hash):
        props_xml = {}
        for field_type in fields_hash:
            if field_type not in cls.supported_field_types:
                pass
            else:
                vals = fields_hash[field_type]
                for field in vals:
                    props_xml['{}:{}'.format(field_type, field)] = _safe_xml_val(vals[field])

        return props_xml

    @classmethod
    def _tostring(cls, root):
        return ET.tostring(root)

    @classmethod
    def fromstring(cls, data):
        """
        Fetch xml.etree.ElementTree for input data

        :param data:   raw xml data
        :returns:      :class:xml.etree.ElementTree
        """
        return ET.fromstring(_prepare_xml_parsing(data))

    @classmethod
    def build_propfind_datas(cls, instr=None, filter_rules=None, fields=None):
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

        root = ET.Element(instr, cls.xml_namespaces_map)
        props = cls._to_fields_list(fields or {})
        if props:
            prop_group = ET.SubElement(root, 'd:prop')
            for prop in props:
                ET.SubElement(prop_group, prop)

        rules = cls._to_field_vals_list(filter_rules or {})
        if rules:
            rule_group = ET.SubElement(root, 'oc:filter-rules')
            for k in rules:
                rule = ET.SubElement(rule_group, k)
                val = rules[k]
                rule.text = _safe_xml_val(val)

        return cls._tostring(root)

    @classmethod
    def build_propupdate_datas(cls, values):
        """
        Build XML datas for a PROPUPDATE querry.

        :param values:       a dict containing values separated by namespace
                             e.g. {'oc': {'favorite': 1}}
        :returns:            xml data (string)
        """
        root = ET.Element('d:propertyupdate', cls.xml_namespaces_map)
        vals = cls._to_field_vals_list(values)
        if vals:
            set_group = ET.SubElement(root, 'd:set')
            val_group = ET.SubElement(set_group, 'd:prop')
            for k in vals:
                val = ET.SubElement(val_group, k)
                val.text = vals[k]

        return cls._tostring(root)

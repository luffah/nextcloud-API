# -*- coding: utf-8 -*-
"""
Generic request/result class (ORM-like objects)
"""
import re
import six
from ..common import build_xml as BuildXML, parse_xml as ParseXML
from .properties import NAMESPACES_MAP, Property
from .item_set import ItemSet
from ..compat import unquote, decode_string, encode_string

ALL_PROPERTIES = {}
RESERVED_KEYS = []

class MetaModel(type):
    """ Meta Property Set : find properties in class """

    @property
    def _properties(cls):
        return [ "%s:%s" % (v.ns, v.xml_key) for v in cls._attrs]

    @property
    def _fields(cls):
        return [v.attr_name for v in cls._attrs]

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        if name not in ALL_PROPERTIES:
            ALL_PROPERTIES[name] = []
        for key, val in attrs.items():
            if name == 'Item' and callable(val):
                RESERVED_KEYS.append(key)
            elif isinstance(val, Property):
                if key in RESERVED_KEYS:
                    raise ValueError(
                        "%s can't be a Property and a method for Item at same time."
                        " See nextcloud.api.model.RESERVED_KEYS." % key)
                val.update_attr_name(key)

                xml_compute_func = val.parse_xml_value
                if isinstance(xml_compute_func, str):
                    val.parse_xml_value = getattr(new_cls, xml_compute_func)

                json_compute_func = val.parse_json_value
                if isinstance(json_compute_func, str):
                    val.parse_json_value = getattr(new_cls, json_compute_func)

                ALL_PROPERTIES[name].append(val)
        new_cls._attrs = ALL_PROPERTIES[name]
        return new_cls


class Item(six.with_metaclass(MetaModel)):
    """
    Set of nextcloud.common.properties.Property
    defined in _attrs class variable.

    The inherited classes can do additionnal complex operations
    if wrapper instance is defined at initialization.
    """
    SUCCESS_STATUS = 'HTTP/1.1 200 OK'
    COLLECTION_RESOURCE_TYPE = 'collection'
    _attrs = []
    _repr_attrs = ['href']

    @classmethod
    def _fetch_properties(cls, key, key_name='xml_key'):
        for k in cls._attrs:
            if getattr(k, key_name, False) == key:
                yield k

    def __get_repr_info__(self):
        values = {}
        for k in self._repr_attrs:
            val = getattr(self, k, None)
            if val is None:
                continue
            if isinstance(val, six.text_type):
                values[k] = repr(encode_string(val))
            else:
                values[k] = repr(val)

        return "{%s}" % ', '.join(
            ["'%s' : %s" % (k, v) for k, v in values.items()]
        )

    def __init__(self, data=None, json_data=None, xml_data=None, wrapper=None):
        self._wrapper = wrapper or getattr(self, '_wrapper', False)
        if xml_data is not None:
            self._parse_xml(xml_data)
        if json_data is not None:
            self._parse_json(json_data)
        if data is not None:
            for k in data:
                self[k] = data[k]

    def __iter__(self):
        """ Return an iterator over properties. """
        for prop in self._attrs:
            yield prop

    def __getitem__(self, key):
        return getattr(self, key, None)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __delitem__(self, key):
        'c.__delitem__(y) <==> del c[y]'
        if key in self._attrs:
            self[key] = None

    def copy(self):
        'Return a shallow copy.'
        return self.__class__(wrapper=self._wrapper, data=self)

    def get(self, key, default=None):
        'Return attribute value or default'
        return getattr(self, key, default)

    def as_dict(self):
        """ Return current instance as a {k: val} dict """
        attrs = [v.attr_name for v in self._attrs]
        return {key: value for key, value in self.__dict__.items() if key in attrs}

    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, self.__get_repr_info__())

    def _parse_json(self, data):
        for attr in self._attrs:
            self[attr.attr_name] = None

        for k in data:
            for prop in type(self)._fetch_properties(k, key_name='json_key'):
                value = prop.get_value(data[k])
                self[prop.attr_name] = value

    def _parse_xml(self, xml_data):
        for attr in self._attrs:
            self[attr.attr_name] = None

        self.href = decode_string(
            unquote(xml_data.find('d:href', NAMESPACES_MAP).text)
        )
        for propstat in xml_data.iter('{DAV:}propstat'):
            if propstat.find('d:status', NAMESPACES_MAP).text != self.SUCCESS_STATUS:
                pass
            else:
                for xml_property in propstat.find('d:prop', NAMESPACES_MAP):
                    property_name = re.sub('{.*}', '', xml_property.tag)
                    for prop in type(self)._fetch_properties(property_name):
                        value = prop.get_value(xml_property)
                        self[prop.attr_name] = value

    @classmethod
    def default_get(cls, key_format='json', **kwargs):
        """
        Get default values

        :param key_format: 'json' or 'xml'
        :param (any):       values to force (python names)
        """
        vals = {getattr(v, '%s_key' % key_format): kwargs.get(v.attr_name, v.default_value)
                for v in cls._attrs if getattr(v, '%s_key' % key_format, False)}
        return vals

    @classmethod
    def build_xml_propfind(cls, instr=None, filter_rules=None, use_default=False, fields=None):
        """see build_xml.build_propfind_datas

        :param instr(str): you can use 'oc:filter-files' or 'd:propfind' (default)
        :param filter_rules : a dict { namespace: {key : value } }
        :param fields: a dict { namespace: [key…] } or a list of attr name
        :param use_default:   True to use all values specified in Model
        """
        def _build_fields_dict(only_required=False, attr_name_list=None):
            _fields = {k: [] for k in NAMESPACES_MAP}
            for attr in cls._attrs:
                if only_required:
                    if not attr.required:
                        continue
                if attr_name_list is not None:
                    if attr.attr_name not in attr_name_list:
                        continue
                if attr.disabled:
                    # warning message if in attr_name_list ?
                    continue
                _fields[attr.ns].append(attr.xml_key)
            return _fields

        if not fields:
            fields = _build_fields_dict(only_required=(not use_default))
        elif isinstance(fields, list):
            fields = _build_fields_dict(attr_name_list=fields)
        if not (fields or filter_rules):
            return None
        return BuildXML.build_propfind_datas(instr=instr, filter_rules=filter_rules,
                                              fields=(fields or {}))

    @classmethod
    def build_xml_propupdate(cls, values):
        """ see build_xml.build_propupdate_datas """
        return BuildXML.build_propupdate_datas(values)

    @classmethod
    def from_response(cls, resp, filtered=None, wrapper=None, multi=None):
        """ Build set of Model instance from a NextcloudResponse """
        response_data = resp.data
        if multi is None:
            if isinstance(response_data, dict):
                # json dict, usually a single result
                multi = False
            elif response_data.startswith('<?xml'):
                # xml, usually a list of results
                multi = True

        if not resp.is_ok:
            resp.data = ItemSet(cls, []) if multi else None
            return resp

        if isinstance(response_data, dict):
            attr_datas = [cls(json_data=response_data, wrapper=wrapper)]
        elif response_data.startswith('<?xml'):
            response_xml_data = ParseXML.fromstring(response_data)

            attr_datas = [cls(xml_data=xml_data, wrapper=wrapper)
                          for xml_data in response_xml_data]
        if not multi:
            resp.data = attr_datas[0] if attr_datas else None
            return resp

        if filtered:
            if callable(filtered):
                attr_datas = [
                    attr_data
                    for attr_data in attr_datas
                    if filtered(attr_data)
                ]
        resp.data = ItemSet(cls, attr_datas)
        return resp

    def as_dict(self):
        """ Return current instance as a {k: val} dict """
        attrs = [v.attr_name for v in self._attrs]
        return {key: value for key, value in self.__dict__.items() if key in attrs}

# -*- coding: utf-8 -*-
"""
Define generic request/result class
common to File and Tag
"""
import re
from nextcloud.common.simplexml import SimpleXml
from nextcloud.common.properties import NAMESPACES_MAP


class PropertySet(object):
    """
    Set of nextcloud.common.properties.Prop
    defined in _attrs class variable.

    The inherited classes can do additionnal complex operations
    if wrapper instance is defined at initialization.
    """
    SUCCESS_STATUS = 'HTTP/1.1 200 OK'
    COLLECTION_RESOURCE_TYPE = 'collection'
    _attrs = []

    @property
    def _fields(self):
        return [v.attr_name for v in self._attrs]

    @property
    def _properties(self):
        return [v.xml_key for v in self._attrs]

    @classmethod
    def _fetch_property(cls, key, attr='xml_key'):
        for k in cls._attrs:
            if getattr(k, attr) == key:
                return k

    def __init__(self, xml_data, init_attrs=False, wrapper=None):
        if init_attrs:
            for attr in self._attrs:
                setattr(self, attr.attr_name, None)

        self._wrapper = wrapper
        self.href = xml_data.find('d:href', NAMESPACES_MAP).text
        for propstat in xml_data.iter('{DAV:}propstat'):
            if propstat.find('d:status', NAMESPACES_MAP).text != self.SUCCESS_STATUS:
                pass
            else:
                for xml_property in propstat.find('d:prop', NAMESPACES_MAP):
                    property_name = re.sub('{.*}', '', xml_property.tag)
                    prop = self._fetch_property(property_name)
                    if not prop:
                        pass
                    else:
                        value = prop.get_value(xml=xml_property)
                        setattr(self, prop.attr_name, value)

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
        """see SimpleXml.build_propfind_datas

        :param use_default:   True to use all values specified in PropertySet
        """
        if use_default:
            if not fields:
                fields = {k: [] for k in NAMESPACES_MAP.keys()}
                for attr in cls._attrs:
                    fields[attr.ns].append(attr.xml_key)

        return SimpleXml.build_propfind_datas(instr=instr, filter_rules=filter_rules,
                                              fields=(fields or {}))

    @classmethod
    def build_xml_propupdate(cls, values):
        """ see SimpleXml.build_propupdate_datas """
        return SimpleXml.build_propupdate_datas(values)

    @classmethod
    def from_response(cls, resp, json_output=None, filtered=None,
                      init_attrs=None, wrapper=None):
        """ Build list of PropertySet from a NextcloudResponse """
        if not resp.is_ok:
            resp.data = None
            return resp
        else:
            response_data = resp.data
            response_xml_data = SimpleXml.fromstring(response_data)
            attr_datas = [cls(xml_data, init_attrs=init_attrs, wrapper=wrapper)
                          for xml_data in response_xml_data]
            if filtered:
                if callable(filtered):
                    attr_datas = [
                        attr_data for attr_data in attr_datas if filtered(attr_data)]
            resp.data = attr_datas if not json_output else [
                attr_data.as_dict() for attr_data in attr_datas]
            return resp

    def as_dict(self):
        """ Return current instance as a {k: val} dict """
        attrs = [v.attr_name for v in self._attrs]
        return {key: value for key, value in self.__dict__.items() if key in attrs}

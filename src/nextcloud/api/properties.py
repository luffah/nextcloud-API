# -*- coding: utf-8 -*-
"""
Define properties types that can be used one OwnCloud/NextCloud elements


How to define a new property namespace. Example:
>>> class NCProp(Property):
>>>    # define the namespace code with the namespace value
>>>     namespace = ('nc', 'http://nextcloud.org/ns')

"""
import six
import xml
from ..common import namming

NAMESPACES_MAP = {}


class MetaProperty(type):
    """ Meta class that register namespaces """
    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        if new_cls.namespace[0]:
            NAMESPACES_MAP[new_cls.namespace[0]] = new_cls.namespace[1]
        return new_cls


class Property(six.with_metaclass(MetaProperty)):
    """
    Define an element property, and naming of resulting python attribute

    :param xml_name:        xml property name (prefixed with 'ns:' i.e. namespace)
    :param json:            json property name
    :param default:         default value (value or function without args)
    :param parse_xml_value: a function that take xml.etree.ElementTree and
                            return value of the property
    :param parse_json_value:a function that take a dict and
                            return value of the property
    :param required (bool): True if the field shall be included by default
    :param disabled (bool): True if the field shall not be used in requests
    """
    namespace = (None, None)

    # pylint: disable=too-many-arguments, invalid-name
    def __init__(self,
                 xml_name=None,
                 json=None,
                 default=None,
                 parse_value=None,
                 parse_xml_value=None,
                 parse_json_value=None,
                 attr_name=None,
                 required=None,
                 disabled=None):
        self.ns = None
        self.xml_key = xml_name
        self.attr_name = attr_name
        self.json_key = json
        self.default_val = default
        self.parse_value = parse_value
        self.parse_xml_value = parse_xml_value
        self.parse_json_value = parse_json_value
        self.required = required
        self.disabled = disabled
        if xml_name:
            if ':' in xml_name:
                (self.ns, self.xml_key) = xml_name.split(':')
            if not self.attr_name:
                self.attr_name = namming.xml_to_py_name(self.xml_key)
        if not self.ns:
            self.ns = self.namespace[0]

    def update_attr_name(self, attr_name):
        """ Setup the python variable name """
        self.attr_name = attr_name
        if self.namespace and not self.xml_key:
            self.xml_key = namming.py_to_xml_name(attr_name)
        if not self.json_key:
            self.json_key = namming.py_to_json_name(attr_name)

    def __repr__(self):
        return "<Property ns={}, xml={}, py={}, json={}>".format(
            self.ns,
            self.xml_key,
            self.attr_name,
            self.json_key
        )

    @property
    def default_value(self):
        """ Fetch default value """
        if callable(self.default_val):
            return self.default_val()
        return self.default_val

    def get_value(self, data=None):
        """
        Fetch value from input data

        :param data: json dict or xml.etree.ElementTree.Element node
        :returns:    python value
        """
        ret = data
        if isinstance(data, dict):
            if self.parse_json_value:
                ret = self.parse_json_value(data)
        elif isinstance(data, xml.etree.ElementTree.Element):
            if self.parse_xml_value:
                ret = self.parse_xml_value(data)
            else:
                ret = data.text
        if ret:
            if self.parse_value:
                ret = self.parse_value(ret)
        return ret


class DProp(Property):
    """ DAV property """
    namespace = ('d', 'DAV:')


class OCProp(Property):
    """ OwnCloud property """
    namespace = ('oc', 'http://owncloud.org/ns')

class NCProp(Property):
    """ NextCloud property """
    namespace = ('nc', 'http://nextcloud.org/ns')

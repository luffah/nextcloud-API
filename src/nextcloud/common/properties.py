# -*- coding: utf-8 -*-
"""
Define properties types that can be used one OwnCloud/NextCloud elements


How to define a new property namespace. Example:
>>> class NCProp(Property):
>>>    # define the namespace code with the namespace value
>>>     namespace = ('nc', 'http://nextcloud.org/ns')
>>>    # choose which attribute name is given by default on PropertySet
>>>    _name_convention = {
>>>        # xml     :  python
>>>        'xmly-attr-name': 'cute_attr_name',
>>>    }  # Note: by default, all '-' are already replaced by '_'

"""
import six

NAMESPACES_MAP = {}
NAMESPACES_CLASSES = {}


class MetaProperty(type):
    def __new__(meta, name, bases, attrs):
        cls = type.__new__(meta, name, bases, attrs)
        if (cls.namespace):
            NAMESPACES_MAP[cls.namespace[0]] = cls.namespace[1]
            NAMESPACES_CLASSES[cls.namespace[0]] = cls
        return cls


class Property(object, six.with_metaclass(MetaProperty)):
    """
    Define an element property, and naming of resulting python attribute

    :param xml_name:        xml property name (prefixed with 'ns:' i.e. namespace)
    :param json:            json property name
    :param default:         default value (value or function without args)
    :param parse_xml_value: a function that take xml.etree.ElementTree and
                            return value of the property
    """
    namespace = None
    _name_convention = {}

    def __init__(self, xml_name, json=None, default=None, parse_xml_value=None):
        if ':' in xml_name:
            (self.ns, self.xml_key) = xml_name.split(':')
            self._name_convention = NAMESPACES_CLASSES[self.ns]
        else:
            self.xml_key = xml_name
            if self.namespace:
                self.ns = self.namespace[0]

        self.attr_name = self._xml_name_to_py_name(self.xml_key)
        self.json_key = json
        self.default_val = default
        self.parse_xml_value = parse_xml_value

    @classmethod
    def _xml_name_to_py_name(cls, name):
        if name in cls._name_convention:
            return cls._name_convention[name]
        else:
            return name.replace('-', '_')

    @classmethod
    def _py_name_to_xml_name(cls, name):
        _reversed_convention = {v: k for k, v in cls._name_convention.items()}
        if name in _reversed_convention:
            return _reversed_convention[name]
        else:
            return name.replace('_', '-')

    @property
    def default_value(self):
        """ Fetch default value """
        if callable(self.default_val):
            return self.default_val()
        else:
            return self.default_val

    def get_value(self, xml=None):
        """
        Fetch value from input data

        :param xml:  xml.etree.ElementTree node
        :returns:    python value
        """
        if xml is not None:
            if self.parse_xml_value:
                return self.parse_xml_value(xml)
            else:
                return xml.text


class DProp(Property):
    """ DAV property """
    namespace = ('d', 'DAV:')

    _name_convention = {
        'getlastmodified': 'last_modified',
        'getetag': 'etag',
        'getcontenttype': 'content_type',
        'resourcetype': 'resource_type',
                        'getcontentlength': 'content_length'
    }

class OCProp(Property):
    """ OwnCloud property """
    namespace = ('oc', 'http://owncloud.org/ns')

    _name_convention = {
        'fileid': 'file_id',
        'checksums': 'check_sums'
    }


class NCProp(Property):
    """ NextCloud property """
    namespace = ('nc', 'http://nextcloud.org/ns')

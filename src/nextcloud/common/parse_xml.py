# -*- coding: utf-8 -*-
"""
XML parser
"""
import xml.etree.ElementTree as ET
from ..compat import encode_string


def _prepare_xml_parsing(string):
    return encode_string(string)


def fromstring(data):
    """
    Fetch xml.etree.ElementTree for input data

    :param data:   raw xml data
    :returns:      :class:xml.etree.ElementTree
    """
    return ET.fromstring(_prepare_xml_parsing(data))


# Note : etree_to_dict is mainly developped for group_folders wrapper v4 which
#        doesn't support json format

def etree_to_dict(element):
    " Get a dict from an element tree "
    return {element.tag: _etree_to_dict(element, element.tag)}


XPATH_KEY_VALUE_DEF = {
    'ocs/data/groups/element': ('group_id', 'permissions', int)
}


def _etree_to_dict(element, xpath):
    # pylint: disable=too-many-locals, too-many-branches, unnecessary-comprehension
    node = dict()

    text = getattr(element, 'text', None)
    child_nodes = {}

    element_childs = [k for k in element]

    if not element_childs and element.tag == 'element':
        return {k: v for k, v in element.items()}

    for child in element_childs:  # element's children
        child_path = xpath + '/' + child.tag
        sub_node = _etree_to_dict(child, child_path)
        if child.tag == 'element':
            if isinstance(sub_node, dict):
                cur_tag = element.tag
                if child_path in XPATH_KEY_VALUE_DEF:
                    id_tag, value_tag, _type = XPATH_KEY_VALUE_DEF[child_path]
                    _key = sub_node.get(id_tag, False)
                    _value = sub_node.get(value_tag, False)
                    if _value:
                        _value = _type(_value)
                else:
                    _key = sub_node.pop('id', False)
                    if not _key:
                        id_tag = cur_tag[:-1] if cur_tag.endswith('s') else cur_tag
                        _key = sub_node.pop('%s_id' % id_tag, False)
                    _value = sub_node
                if not _key:
                    _key = child.tag
                child_nodes[_key] = _value
            elif isinstance(sub_node, list):
                child_nodes = sub_node
        else:
            child_nodes.setdefault(child.tag, []).append(sub_node)

    if not element_childs:
        if element.tag == 'data':
            if text == '0' or not text:
                text = False
            elif text == '1':
                text = True
        if text is None:
            text = []
        return text

    if isinstance(child_nodes, list):
        if len(child_nodes) == 1:
            return child_nodes[0]
        return child_nodes

    # convert all single-element lists into non-lists
    for key, value in child_nodes.items():
        if isinstance(value, list):
            if len(value) == 1:
                child_nodes[key] = value[0]

    node.update(child_nodes.items())

    return node

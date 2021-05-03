# -*- coding: utf-8 -*-
"""
SystemTags API wrapper
See https://doc.owncloud.com/server/developer_manual/webdav_api/tags.html
"""
import json
from nextcloud.base import WebDAVApiWrapper
from nextcloud.common.collections import PropertySet
from nextcloud.common.properties import Property as Prop


class Tag(PropertySet):
    _attrs = [
        Prop('oc:id'),
        Prop('oc:display-name', json='name', default='default_tag_name'),
        Prop('oc:user-visible', json='userVisible', default=True),
        Prop('oc:can-assign', json='canAssign', default=True),
        Prop('oc:user-assignable', json='userAssignable', default=True)
    ]


class SystemTags(WebDAVApiWrapper):
    """ SystemTags API wrapper """
    API_URL = '/remote.php/dav/systemtags'
    JSON_ABLE = True

    def get_sytemtag(self, name, fields=None, json_output=None):
        if not fields:
            fields = Tag._fields
        resp = self.requester.propfind(data=Tag.build_xml_propfind(
            fields={'oc': ['display-name'] + fields}))
        if json_output is None:
            json_output = self.json_output
        return Tag.from_response(resp,
                                 json_output=json_output,
                                 init_attrs=True,
                                 filtered=(lambda t: t.display_name == name))

    def get_systemtags(self):
        """
        Get list of all tags

        :returns: requester response with <list>Tag in data
        """
        resp = self.requester.propfind(
            data=Tag.build_xml_propfind(use_default=True))
        return Tag.from_response(resp, json_output=(self.json_output))

    def create_systemtag(self, name, **kwargs):
        """
        Create a new system tag from name.

        :param name:  tag name
        :returns: requester response with tag id as data
        """
        data = (Tag.default_get)(name=name, **kwargs)
        resp = self.requester.post(data=(json.dumps(data)), headers={
                                   'Content-Type': 'application/json'})
        if resp.is_ok:
            resp.data = int(
                resp.raw.headers['Content-Location'].split('/')[(-1)])
        return resp

    def delete_systemtag(self, name=None, tag_id=None):
        """
        Delete systemtag
        
        :param name (str): tag name, not required it tag_id is provided
        :tag_id (int): tag id, not required if name is provided

        :returns: requester response
        """
        if not tag_id:
            resp = self.get_sytemtag(name, ['id'], json_output=False)
            if resp.data:
                tag_id = resp.data[0].id
        elif tag_id:
            resp = self.requester.delete(url=(str(tag_id)))
        return resp


class SystemTagsRelation(WebDAVApiWrapper):
    """ SystemTagsRelation API wrapper """
    API_URL = '/remote.php/dav/systemtags-relations/files'
    JSON_ABLE = True
    REQUIRE_CLIENT = True

    def _get_fileid_from_path(self, path):
        """ Tricky function to fetch file """
        resp = self.client.get_file_property(path, 'fileid')
        id_ = None
        if resp.data:
            id_ = int(resp.data)
        return id_

    def _get_systemtag_id_from_name(self, name):
        resp = self.client.get_sytemtag(name, ['id'], json_output=False)
        tag_id = None
        if resp.data:
            tag_id = int(resp.data[0].id)
        return tag_id

    def _default_get_file_id(self, vals):
        path = vals.get('path', None)
        if not path:
            raise ValueError('Insufficient infos about the file')
        return self._get_fileid_from_path(path)

    def _default_get_tag_id(self, vals):
        tag_name = vals.get('tag_name', None)
        if not tag_name:
            raise ValueError('Insufficient infos about the tag')
        return self._get_systemtag_id_from_name(tag_name)

    def get_systemtags_relation(self, file_id=None, **kwargs):
        """
        Get all tags from a given file/folder

        :param file_id (int): file id found from file object
        :param path (str): if no file_id provided, path to file/folder

        :returns: requester response with <list>Tag in data
        """
        file_id, = self._arguments_get(['file_id'], locals())
        data = Tag.build_xml_propfind()
        resp = self.requester.propfind(additional_url=file_id, data=data)
        return Tag.from_response(resp, json_output=(self.json_output))

    def delete_systemtags_relation(self, file_id=None, tag_id=None, **kwargs):
        """
        Delete a tag from a given file/folder

        :param file_id (int): id found in file object
        :param tag_id  (int): id found in tag object
        :param path (str): if unknown file_id, path to file/folder
        :param tag_name (str): if unknown tag_id, tag_name to search or create

        :returns: requester response
        """
        file_id, tag_id = self._arguments_get([
            'file_id', 'tag_id'], locals())
        resp = self.requester.delete(url=('{}/{}'.format(file_id, tag_id)))
        return resp

    def add_systemtags_relation(self, file_id=None, tag_id=None, **kwargs):
        """
        Add a tag from a given file/folder

        :param file_id (int): id found in file object
        :param tag_id  (int): id found in tag object
        :param path (str): if unknown file_id, path to file/folder
        :param tag_name (str): if unknown tag_id, tag_name to search or create

        :returns: requester response
        """
        file_id, tag_id = self._arguments_get([
            'file_id', 'tag_id'], locals())
        if not tag_id:
            if 'tag_name' in kwargs:
                resp = self.client.create_systemtag(kwargs['tag_name'])
                if not resp.is_ok:
                    return resp
                tag_id = resp.data
        if not file_id:
            raise ValueError('No file found')
        data = Tag.build_xml_propfind()
        resp = self.requester.put(url=('{}/{}'.format(file_id, tag_id)))
        return resp

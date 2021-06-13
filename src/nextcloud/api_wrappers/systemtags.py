# -*- coding: utf-8 -*-
"""
SystemTags API wrapper
See https://doc.owncloud.com/server/developer_manual/webdav_api/tags.html
"""
import json
from ..base import WebDAVApiWrapper
from ..api import Item
from ..api.properties import OCProp
from . import webdav


class Tag(Item):
    """ Define a Tag properties"""
    _repr_attrs = ['href', 'display_name']

    id = OCProp(parse_value=int, required=True)
    display_name = OCProp(json='name', default='default_tag_name',
                          required=True)
    user_visible = OCProp(json='userVisible', default=True)
    can_assign = OCProp(json='canAssign', default=True)
    user_assignable = OCProp(json='userAssignable', default=True)

    def get_related_files(self, path=''):
        """
        Get files related to current tag
        :param path: (optionnal) a path to search in
        """
        ret = self._wrapper.client.fetch_files_with_filter(
            path=path,
            filter_rules={'oc': {'systemtag': self.id}}
        )
        return ret.data or []

    def delete(self):
        """
        Delete current tag

        :returns: True if success
        """
        ret = self._wrapper.delete_systemtag(tag_id=self.id)
        return ret.is_ok


class File(webdav.File):
    """ Add method to file object """

    def _get_file_kwargs(self):
        kwargs = {}
        if not getattr(self, 'file_id', False):
            kwargs['path'] = self._get_remote_path()
        else:
            kwargs['file_id'] = self.file_id
        return kwargs

    def get_tags(self):
        """
        Get tags related to current file
        :returns :  list<Tag>
        """
        kwargs = self._get_file_kwargs()
        return self._wrapper.client.get_systemtags_relation(**kwargs)

    def add_tag(self, **kwargs):
        """
        Assign tag to the current file
        :param tag_id:   tag id
        :param tag_name: tag name (if tag_id in not provided)
        :returns : False if failure
        """
        kwargs.update(self._get_file_kwargs())
        resp = self._wrapper.client.add_systemtags_relation(**kwargs)
        return resp.is_ok

    def remove_tag(self, **kwargs):
        """
        Unassign tag to the current file
        :param tag_id:   tag id
        :param tag_name: tag name (if tag_id in not provided)
        :returns : False if failure
        """
        kwargs.update(self._get_file_kwargs())
        resp = self._wrapper.client.remove_systemtags_relation(**kwargs)
        return resp.is_ok


webdav.File = File


class SystemTags(WebDAVApiWrapper):
    """ SystemTags API wrapper """
    API_URL = '/remote.php/dav/systemtags'

    def get_systemtags(self):
        """
        Get list of all tags

        :returns: list<Tag>
        """
        return self.get_objs_from_response(
            self.fetch_systemtags()
        )

    def get_systemtag(self, name, create=False, **kwargs):
        """
        Return a nammed tag

        :param name(str): tag name
        :param create(bool): create the tag before getting it (default False)
        :returns: Tag
        """
        if create:
            resp = self.create_systemtag(name, **kwargs)
            if resp.is_ok:
                vals = {
                    'id':resp.data, 'display_name': name
                }
                vals.update(kwargs)
                return Tag(vals)
            return None
        return self.get_objs_from_response(
            self.fetch_systemtag(name),
            one=True
        )

    def fetch_systemtag(self, name, fields=None):
        """
        Get attributes of a nammed tag

        :param name (str): tag name
        :param fields (<list>str): field names
        :returns: requester response with list<Tag> in data
        """
        resp = self.requester.propfind(
            data=Tag.build_xml_propfind(fields=(
                {'oc': ['display-name'] + fields} if fields else None
            ), use_default=True)
        )
        return Tag.from_response(resp, wrapper=self,
                                 filtered=lambda t: t.display_name == name)

    def fetch_systemtags(self):
        """
        List of all tags

        :returns: requester response with list<Tag> in data
        """
        resp = self.requester.propfind(
            data=Tag.build_xml_propfind(use_default=True)
        )
        return Tag.from_response(resp, wrapper=self)

    def create_systemtag(self, name, **kwargs):
        """
        Create a new system tag from name.

        :param name:  tag name
        :returns: requester response with tag id as data
        """
        data = Tag.default_get(display_name=name, **kwargs)
        resp = self.requester.post(
            data=json.dumps(data),
            headers={
                'Content-Type': 'application/json'
            })
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
            resp = self.fetch_systemtag(name, ['id'])
            if resp.data:
                tag_id = resp.data[0].id
            if not tag_id:  # lint only
                return resp
        resp = self.requester.delete(url=(str(tag_id)))
        return resp


class SystemTagsRelation(WebDAVApiWrapper):
    """ SystemTagsRelation API wrapper """
    API_URL = '/remote.php/dav/systemtags-relations/files'

    def _get_fileid_from_path(self, path):
        """ Tricky function to fetch file """
        resp = self.client.get_file_property(path, 'fileid')
        _id = None
        if resp.data:
            _id = int(resp.data)
        return _id

    def _get_systemtag_id_from_name(self, name):
        resp = self.client.fetch_systemtag(name, ['id'])
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

        :returns: requester response with list<Tag> in data
        """
        return SystemTags.get_objs_from_response(
            self.fetch_systemtags_relation(file_id=file_id, **kwargs),
            skip_url=self.API_URL + '/' + str(file_id) + '/'
        )

    def fetch_systemtags_relation(self, file_id=None, **kwargs):
        """
        Get all tags from a given file/folder

        :param file_id (int): file id found from file object
        :param path (str): if no file_id provided, path to file/folder

        :returns: requester response with list<Tag> in data
        """
        file_id = self._default_get('file_id', dict(file_id=file_id, **kwargs))
        data = Tag.build_xml_propfind(use_default=True)
        resp = self.requester.propfind(url=file_id, data=data)
        return Tag.from_response(resp, wrapper=self)

    def remove_systemtags_relation(self, file_id=None, tag_id=None, **kwargs):
        """
        Remove a tag from a given file/folder

        :param file_id (int): id found in file object
        :param tag_id  (int): id found in tag object
        :param path (str): if unknown file_id, path to file/folder
        :param tag_name (str): if unknown tag_id, tag_name to search or create

        :returns: requester response
        """
        file_id = self._default_get('file_id', dict(file_id=file_id, **kwargs))
        tag_id = self._default_get('tag_id', dict(tag_id=tag_id, **kwargs))
        if not file_id:
            raise ValueError('No file found')
        if not tag_id:
            raise ValueError('No tag found (%s)' %
                             kwargs.get('tag_name', None))
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
        file_id = self._default_get('file_id', dict(file_id=file_id, **kwargs))
        tag_id = self._default_get('tag_id', dict(tag_id=tag_id, **kwargs))
        if not file_id:
            raise ValueError('No file found')
        if not tag_id:
            data = Tag.default_get(
                display_name=kwargs.get('tag_name'), **kwargs)
            resp = self.requester.post_json(
                url=file_id,
                data=json.dumps(data)
            )
            # resp = self.client.create_systemtag(kwargs['tag_name'])
            # if not resp.is_ok:
            return resp
            # tag_id = resp.data
        resp = self.requester.put(url='{}/{}'.format(file_id, tag_id))
        return resp

# -*- coding: utf-8 -*-
"""
WebDav API wrapper
See https://docs.nextcloud.com/server/14/developer_manual/client_apis/WebDAV/index.html
    https://doc.owncloud.com/server/developer_manual/webdav_api/search.html
    https://docs.nextcloud.com/server/14/developer_manual/client_apis/WebDAV/search.html

Not implemented yet:
   - search feature
   - trash
   - versions
   - chunked file upload
"""
# implementing dav search
# -> add a function to build xml search
#   see ../common/build_xml.py and ../api/model.py
import re
import os
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

import xml.etree.ElementTree as ET
from datetime import datetime
from ..base import WebDAVApiWrapper
from ..exceptions import NextCloudError
from ..api.model import Item
from ..api.properties import NAMESPACES_MAP, DProp, OCProp, NCProp
from ..common.value_parsing import (
    timestamp_to_epoch_time,
    datetime_to_timestamp
)


class NextCloudDirectoryNotEmpty(NextCloudError):
    """ When you try to remove a folder that is not empty"""


class NextCloudFileConflict(NextCloudError):
    """ When you try to create a File that alreay exists """


class File(Item):
    """
    Define properties on a WebDav file/folder

    Additionnally, provide an objective CRUD API
    (that probably consume more energy than fetching specific attributes)

    Example :
    >>> root = nxc.get_folder()  # get root
    >>> def _list_rec(d, indent=""):
    >>>     # list files recursively
    >>>     print("%s%s%s" % (indent, d.basename(), '/' if d.isdir() else ''))
    >>>     if d.isdir():
    >>>         for i in d.list():
    >>>             _list_rec(i, indent=indent+"  ")
    >>>
    >>> _list_rec(root)
    """

    @staticmethod
    def _extract_resource_type(file_property):
        file_type = list(file_property)
        if file_type:
            return re.sub('{.*}', '', file_type[0].tag)
        return None

    last_modified = DProp('getlastmodified')
    etag = DProp('getetag')
    content_type = DProp('getcontenttype')
    resource_type = DProp('resourcetype',
                          parse_xml_value='_extract_resource_type')
    content_length = DProp('getcontentlength')
    id = OCProp()
    file_id = OCProp('fileid')
    favorite = OCProp()
    comments_href = OCProp()
    comments_count = OCProp()
    comments_unread = OCProp()
    owner_id = OCProp()
    owner_display_name = OCProp()
    share_types = OCProp()
    check_sums = OCProp('checksums')
    size = OCProp()
    href = OCProp()
    has_preview = NCProp()

    def isfile(self):
        """ say if the file is a file /!\\ ressourcetype property shall be loaded """
        return not self.resource_type

    def isroot(self):
        """ say if the file is a directory /!\\ ressourcetype property shall be loaded """
        return not self.get_relative_path().replace('/', '')

    def isdir(self):
        """ say if the file is a directory /!\\ ressourcetype property shall be loaded """
        return self.resource_type == self.COLLECTION_RESOURCE_TYPE

    def get_relative_path(self):
        """ get path relative to user root """
        return self._wrapper.get_relative_path(self.href)

    def _get_remote_path(self, path=None):
        _url = self.get_relative_path()
        return '/'.join([_url, path]) if path else _url

    def basename(self):
        """ basename """
        _path = self._get_remote_path()
        return _path.split('/')[-2] if _path.endswith('/') else _path.split('/')[-1]

    def dirname(self):
        """ dirname """
        _path = self._get_remote_path()
        return '/'.join(_path.split('/')[:-2]) if _path.endswith('/') else '/'.join(_path.split('/')[:-1])

    def __eq__(self, b):
        return self.href == b.href

    # MINIMAL SET OF CRUD OPERATIONS
    def get_folder(self, path=None, all_properties=False):
        """
        Get folder (see WebDav wrapper)
        :param path: if empty list current dir
        :param all_properties: fetch all properties (default False)
        :returns: a folder (File object)

        Note : To check if sub folder exists, use get_file method
        """
        return self._wrapper.get_folder(self._get_remote_path(path),
                                        all_properties=all_properties)

    def get_file(self, path=None, all_properties=False):
        """
        Get file (see WebDav wrapper)
        :param path: if empty, get current file
        :param all_properties: fetch all properties (default False)
        :returns: a file or folder (File object)
        """
        return self._wrapper.get_file(self._get_remote_path(path),
                                      all_properties=all_properties)

    def list(self, subpath='', filter_rules=None, all_properties=False):
        """
        List folder (see WebDav wrapper)
        :param subpath: if empty list current dir
        :param all_properties: fetch all properties (default False)
        :returns: list of Files
        """
        if filter_rules:
            resp = self._wrapper.fetch_files_with_filter(
                path=self._get_remote_path(subpath),
                filter_rules=filter_rules
            )
        else:
            resp = self._wrapper.list_folders(
                self._get_remote_path(subpath),
                depth=1,
                all_properties=all_properties
            )
        if resp.is_ok and resp.data:
            _dirs = resp.data
            # remove current dir
            if _dirs[0] == self:
                _dirs = _dirs[1:]
            return _dirs
        return []

    def upload_file(self, local_filepath, name, timestamp=None):
        """
        Upload file (see WebDav wrapper)
        :param local_filepath: path of the local file
        :param name: name of the new file
        :param timestamp (int): timestamp of upload file. If None, get time by local file.
        :returns: True if success
        """
        resp = self._wrapper.upload_file(local_filepath,
                                         self._get_remote_path(name),
                                         timestamp=timestamp)
        return resp.is_ok

    def upload_file_contents(self, file_contents, name=None, timestamp=None):
        """
        Upload file content (see WebDav wrapper)
        :param file_contents: binary content of the file
        :param name: name of the new file (current file if empty)
        :param timestamp (int):  mtime of upload file
        :returns: True if success
        """
        resp = self._wrapper.upload_file_contents(file_contents,
                                                  self._get_remote_path(name),
                                                  timestamp=timestamp)
        return resp.is_ok

    def download(self, name=None, target_dir=None):
        """
        Download file (see WebDav wrapper)
        :param name: name of the new file
        :returns: True if success
        """
        path = self._get_remote_path(name)
        target_path, _file_info = self._wrapper.download_file(path,
                                                              target_dir=target_dir)
        assert os.path.isfile(target_path), "Download failed"
        return target_path

    def isempty(self):
        """
        Say if a folder is emty (always False if not a directory)
        :returns: True if current dir is empty
        """
        if not self.isdir():
            return False
        return not self.list()

    def delete(self, subpath='', recursive=False):
        """
        Delete file or folder (see WebDav wrapper)
        :param subpath: if empty, delete current file
        :param recursive: delete recursively
        :returns: True if success
        """
        if recursive:
            resp = self._wrapper.delete_path(self._get_remote_path(subpath))
        else:
            if subpath:
                _file = self.get_file(subpath, all_properties=False)
                return _file.delete(recursive=recursive)
            if not self.isempty():
                raise NextCloudDirectoryNotEmpty(self.get_relative_path())
            return self.delete(recursive=True)

        return resp.is_ok


class WebDAV(WebDAVApiWrapper):
    """ WebDav API wrapper """
    API_URL = "/remote.php/dav/files"

    def _get_path(self, path):
        if path:
            return '/'.join([self.client.user, path]).replace('//', '/')
        return self.client.user

    def list_folders(self, path=None, depth=1, all_properties=False,
                     fields=None):
        """
        Get path files list with files properties with given depth
        (for current user)

        Args:
            path (str/None): files path
            depth (int): depth of listing files (directories content for example)
            all_properties (bool): list all available file properties in Nextcloud
            fields (str list): file properties to fetch

        Returns:
            list of File objects
        """
        data = File.build_xml_propfind(
            use_default=all_properties,
            fields=fields
        ) if (fields or all_properties) else None
        resp = self.requester.propfind(self._get_path(path),
                                       headers={'Depth': str(depth)},
                                       data=data)
        return File.from_response(resp, wrapper=self)

    def download_file(self, path, target_dir=None):
        """
        Download file by path (for current user)
        File will be saved to working directory
        path argument must be valid file path
        Modified time of saved file will be synced with the file properties in Nextcloud

        Exception will be raised if:
            * path doesn't exist,
            * path is a directory, or if
            * file with same name already exists in working directory

        Args:
            path (str): file path

        Returns:
            a tuple (target_path, File object)
        """
        if not target_dir:
            target_dir = './'
        filename = path.split('/')[(-1)] if '/' in path else path
        file_data = self.get_file(path)
        if not file_data:
            raise ValueError("Given path doesn't exist")
        file_resource_type = file_data.resource_type
        if file_resource_type == File.COLLECTION_RESOURCE_TYPE:
            raise ValueError("This is a collection, please specify file path")
        if filename in os.listdir(target_dir):
            raise ValueError(
                "File with such name already exists in this directory")
        filename = os.path.join(target_dir, filename)
        res = self.requester.download(self._get_path(path))
        with open(filename, 'wb') as f:
            f.write(res.data)

        # get timestamp of downloaded file from file property on Nextcloud
        # If it succeeded, set the timestamp to saved local file
        # If the timestamp string is invalid or broken, the timestamp is downloaded time.
        file_timestamp_str = file_data.last_modified
        file_timestamp = timestamp_to_epoch_time(file_timestamp_str)
        if isinstance(file_timestamp, int):
            os.utime(filename, (
                datetime_to_timestamp(datetime.now()),
                file_timestamp))
        return (filename, file_data)

    def upload_file(self, local_filepath, remote_filepath, timestamp=None):
        """
        Upload file to Nextcloud storage

        Args:
            local_filepath (str): path to file on local storage
            remote_filepath (str): path where to upload file on Nextcloud storage
            timestamp (int): timestamp of upload file. If None, get time by local file.

        Returns:
            requester response
        """
        with open(local_filepath, 'rb') as f:
            file_contents = f.read()
        if timestamp is None:
            timestamp = int(os.path.getmtime(local_filepath))
        return self.upload_file_contents(file_contents, remote_filepath, timestamp)

    def upload_file_contents(self, file_contents, remote_filepath, timestamp=None):
        """
        Upload file to Nextcloud storage

        Args:
            file_contents (bytes): Bytes the file to be uploaded consists of
            remote_filepath (str): path where to upload file on Nextcloud storage
            timestamp (int):  mtime of upload file

        Returns:
            requester response
        """
        return self.requester.put_with_timestamp(
            self._get_path(remote_filepath), data=file_contents, timestamp=timestamp)

    def create_folder(self, folder_path):
        """
        Create folder on Nextcloud storage

        Args:
            folder_path (str): folder path

        Returns:
            requester response
        """
        return self.requester.make_collection(self._get_path(folder_path))

    def assure_folder_exists(self, folder_path):
        """
        Create folder on Nextcloud storage, don't do anything if the folder already exists.
        Args:
            folder_path (str): folder path
        Returns:
            requester response
        """
        self.create_folder(folder_path)
        return True

    def assure_tree_exists(self, tree_path):
        """
        Make sure that the folder structure on Nextcloud storage exists
        Args:
            folder_path (str): The folder tree
        Returns:
            requester response
        """
        tree = pathlib.PurePath(tree_path)
        parents = list(tree.parents)
        ret = True
        subfolders = parents[:-1][::-1] + [tree]
        for subf in subfolders:
            ret = self.assure_folder_exists(str(subf))

        return ret

    def delete_path(self, path):
        """
        Delete file or folder with all content of given user by path

        Args:
            path (str): file or folder path to delete

        Returns:
            requester response
        """
        return self.requester.delete(url=self._get_path(path))

    def move_path(self, path, destination_path, overwrite=False):
        """
        Move file or folder to destination

        Args:
            path (str): file or folder path to move
            destionation_path (str): destination where to move
            overwrite (bool): allow destination path overriding

        Returns:
            requester response
        """
        return self.requester.move(url=self._get_path(path),
                                   destination=self._get_path(
                                       destination_path),
                                   overwrite=overwrite)

    def copy_path(self, path, destination_path, overwrite=False):
        """
        Copy file or folder to destination

        Args:
            path (str): file or folder path to copy
            destionation_path (str): destination where to copy
            overwrite (bool): allow destination path overriding

        Returns:
            requester response
        """
        return self.requester.copy(url=self._get_path(path),
                                   destination=self._get_path(
                                       destination_path),
                                   overwrite=overwrite)

    def set_file_property(self, path, update_rules):
        """
        Set file property

        Args:
            path (str): file or folder path to make favorite
            update_rules : a dict { namespace: {key : value } }

        Returns:
            requester response with list<File> in data

        Note :
            check keys in nextcloud.common.properties.NAMESPACES_MAP for namespace codes
            check object property xml_name for property name
        """
        data = File.build_xml_propupdate(update_rules)
        return self.requester.proppatch(self._get_path(path), data=data)

    def fetch_files_with_filter(self, path='', filter_rules=''):
        """
        List files according to a filter

        Args:
            path (str): file or folder path to search
            filter_rules : a dict { namespace: {key : value } }

        Returns:
            requester response with list<File> in data

        Note :
            check keys in nextcloud.common.properties.NAMESPACES_MAP for namespace codes
            check object property xml_name for property name
        """
        data = File.build_xml_propfind(
            instr='oc:filter-files', filter_rules=filter_rules)
        resp = self.requester.report(self._get_path(path), data=data)
        return File.from_response(resp, wrapper=self)

    def set_favorites(self, path):
        """
        Set files of a user favorite

        Args:
            path (str): file or folder path to make favorite

        Returns:
            requester response
        """
        return self.set_file_property(path, {'oc': {'favorite': 1}})

    def list_favorites(self, path=''):
        """
        List favorites (files) of the user

        Args:
            path (str): file or folder path to search favorite

        Returns:
            requester response with list<File> in data
        """
        return self.fetch_files_with_filter(path, {'oc': {'favorite': 1}})

    def get_file_property(self, path, field, ns='oc'):
        """
        Fetch asked properties from a file path.

        Args:
            path (str): file or folder path to make favorite
            field (str): field name

        Returns:
            requester response with asked value in data
        """
        if ':' in field:
            ns, field = field.split(':')
        get_file_prop_xpath = '{DAV:}propstat/d:prop/%s:%s' % (ns, field)
        data = File.build_xml_propfind(fields={ns: [field]})
        resp = self.requester.propfind(self._get_path(path), headers={'Depth': str(0)},
                                       data=data)
        response_data = resp.data
        resp.data = None
        if not resp.is_ok:
            return resp

        response_xml_data = ET.fromstring(response_data)
        for xml_data in response_xml_data:
            for prop in xml_data.findall(get_file_prop_xpath,
                                         NAMESPACES_MAP):
                resp.data = prop.text
            break

        return resp

    def get_file(self, path, all_properties=False):
        """
        Return the File object associated to the path

        :param path: path to the file
        :returns: File object or None
        """
        resp = self.client.list_folders(
            path, all_properties=all_properties, depth=0)
        if resp.is_ok:
            if resp.data:
                return resp.data[0]
        return None

    def get_folder(self, path=None, all_properties=False):
        """
        Return the File object associated to the path
        If the file (folder or 'collection') doesn't exists, create it.

        :param path: path to the file/folder, if empty use root
        :returns: File object
        """
        fileobj = self.get_file(path, all_properties=all_properties)
        if fileobj:
            if not fileobj.isdir():
                raise NextCloudFileConflict(fileobj.href)
        else:
            self.client.create_folder(path)
            fileobj = self.get_file(path, all_properties=all_properties)

        return fileobj

    def get_relative_path(self, href):
        """
        Returns relative (to application / user) path

        :param href(str):  file href
        :returns   (str):  relative path
        """
        _app_root = '/'.join([self.API_URL, self.client.user])
        return href[len(_app_root):]

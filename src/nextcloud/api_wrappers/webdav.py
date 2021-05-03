# -*- coding: utf-8 -*-
"""
WebDav API wrapper
See https://doc.owncloud.com/server/developer_manual/webdav_api/tags.html
"""
import re
import os
try:
    import pathlib
except:
    import pathlib2 as pathlib

import xml.etree.ElementTree as ET
from datetime import datetime
from nextcloud.base import WebDAVApiWrapper
from nextcloud.common.collections import PropertySet
from nextcloud.common.properties import Property as Prop, NAMESPACES_MAP
from nextcloud.common.value_parsing import timestamp_to_epoch_time


class File(PropertySet):
    _attrs = [
        Prop('d:getlastmodified'),
        Prop('d:getetag'),
        Prop('d:getcontenttype'),
        Prop('d:resourcetype', parse_xml_value=(
            lambda p: File._extract_resource_type(p))),
        Prop('d:getcontentlength'),
        Prop('oc:id'),
        Prop('oc:fileid'),
        Prop('oc:favorite'),
        Prop('oc:comments-href'),
        Prop('oc:comments-count'),
        Prop('oc:comments-unread'),
        Prop('oc:owner-id'),
        Prop('oc:owner-display-name'),
        Prop('oc:share-types'),
        Prop('oc:checksums'),
        Prop('oc:size'),
        Prop('oc:href'),
        Prop('nc:has-preview')
    ]

    @staticmethod
    def _extract_resource_type(file_property):
        file_type = list(file_property)
        if file_type:
            return re.sub('{.*}', '', file_type[0].tag)
        return None

    def isfile(self):
        """ say if the file is a file /!\\ ressourcetype property shall be loaded """
        return not self.resource_type

    def isdir(self):
        """ say if the file is a directory /!\\ ressourcetype property shall be loaded """
        return self.resource_type == self.COLLECTION_RESOURCE_TYPE


class WebDAV(WebDAVApiWrapper):
    """ WebDav API wrapper """
    API_URL = "/remote.php/dav/files"

    def _get_path(self, path):
        if path:
            return '/'.join([self.client.user, path]).replace('//', '/')
        else:
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
            list of dicts if json_output
            list of File objects if not json_output
        """
        data = File.build_xml_propfind(
            use_default=all_properties,
            fields=fields
        ) if (fields or all_properties) else None
        resp = self.requester.propfind(additional_url=self._get_path(path),
                                       headers={'Depth': str(depth)},
                                       data=data)
        return File.from_response(resp, json_output=(self.json_output))

    def download_file(self, path):
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
            None
        """
        filename = path.split('/')[(-1)] if '/' in path else path
        file_data = self.list_folders(path=path, depth=0)
        if not file_data:
            raise ValueError("Given path doesn't exist")
        file_resource_type = (file_data.data[0].get('resource_type')
                              if self.json_output
                              else file_data.data[0].resource_type)
        if file_resource_type == File.COLLECTION_RESOURCE_TYPE:
            raise ValueError("This is a collection, please specify file path")
        if filename in os.listdir('./'):
            raise ValueError( "File with such name already exists in this directory")
        res = self.requester.download(self._get_path(path))
        with open(filename, 'wb') as f:
            f.write(res.data)

        # get timestamp of downloaded file from file property on Nextcloud
        # If it succeeded, set the timestamp to saved local file
        # If the timestamp string is invalid or broken, the timestamp is downloaded time.
        file_timestamp_str = (file_data.data[0].get('last_modified')
                              if self.json_output
                              else file_data.data[0].last_modified)
        file_timestamp = timestamp_to_epoch_time(file_timestamp_str)
        if isinstance(file_timestamp, int):
            os.utime(filename, (datetime.now().timestamp(), file_timestamp))

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
        return self.requester.put_with_timestamp((self._get_path(remote_filepath)), data=file_contents,
                                                 timestamp=timestamp)

    def create_folder(self, folder_path):
        """
        Create folder on Nextcloud storage

        Args:
            folder_path (str): folder path

        Returns:
            requester response
        """
        return self.requester.make_collection(additional_url=(self._get_path(folder_path)))

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
                                   destination=self._get_path(destination_path),
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
                                   destination=self._get_path(destination_path),
                                   overwrite=overwrite)

    def set_favorites(self, path):
        """
        Set files of a user favorite

        Args:
            path (str): file or folder path to make favorite

        Returns:
            requester response
        """
        data = File.build_xml_propupdate({'oc': {'favorite': 1}})
        return self.requester.proppatch(additional_url=self._get_path(path), data=data)

    def list_favorites(self, path=''):
        """
        List favorites (files) of the user

        Args:
            path (str): file or folder path to make favorite

        Returns:
            requester response with <list>File in data
        """
        data = File.build_xml_propfind(
            instr='oc:filter-files', filter_rules={'oc': {'favorite': 1}})
        resp = self.requester.report(additional_url=self._get_path(path), data=data)
        return File.from_response(resp, json_output=self.json_output)

    def get_file_property(self, path, field, tag='oc'):
        """
        Fetch asked properties from a file path.

        Args:
            path (str): file or folder path to make favorite
            field (str): field name

        Returns:
            requester response with asked value in data
        """
        if ':' in field:
            tag, field = field.split(':')
        get_file_prop_xpath = '{DAV:}propstat/d:prop/%s:%s' % (tag, field)
        data = File.build_xml_propfind(fields={tag: [field]})
        resp = self.requester.propfind(additional_url=(self._get_path(path)), headers={'Depth': str(0)},
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

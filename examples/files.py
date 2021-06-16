#!/usr/bin/python3
import os
import sys

from pprint import pprint

# in this example we disable SSL
import urllib3
urllib3.disable_warnings()

from nextcloud import NextCloud

NEXTCLOUD_URL = "http://{}:80".format(os.environ['NEXTCLOUD_HOSTNAME'])
NEXTCLOUD_USERNAME = os.environ.get('NEXTCLOUD_ADMIN_USER')
NEXTCLOUD_PASSWORD = os.environ.get('NEXTCLOUD_ADMIN_PASSWORD')


# see api_wrappers/webdav.py File definition to see attributes of a file
# see api_wrappers/systemtags.py Tag definition to see attributes of a tag
with NextCloud(
        NEXTCLOUD_URL,
        user=NEXTCLOUD_USERNAME,
        password=NEXTCLOUD_PASSWORD,
        session_kwargs={
            'verify': False  # to disable ssl
            }) as nxc:
    # list folder (get file path, file_id, and ressource_type that say if the file is a folder)
    pprint(nxc.list_folders('/').data)
    # list folder with additionnal infos (the owner, if the file is a favorite…)
    pprint(nxc.list_folders('/', all_properties=True).data)
    # list folder content of another user
    pprint(nxc.with_auth(
        user="test",
        password="test_password"
        ).list_folders('/').data)

    # get activity
    pprint(nxc.get_activities('files'))

    # list all files
    root = nxc.get_folder()  # get root
    def _list_rec(d, indent=""):
        # list files recursively
        print("%s%s%s" % (indent, d.basename(), '/' if d.isdir() else ''))
        if d.isdir():
            for i in d.list():
                _list_rec(i, indent=indent+"  ")

    _list_rec(root)

    # fetch an uniq property (in a file object) // not optimal
    pprint(nxc.get_file('/Projet test/Nextcloud Manual.pdf', 'owner_display_name'))

    # get favorite
    pprint(nxc.list_favorites().data)

    # upload
    pprint(nxc.create_folder('testdir_nextcloud').data)
    pprint(nxc.upload_file('localfile.txt', 'testdir_nextcloud/localfilesend.txt').data)

    # download
    f = nxc.get_file('test.md')
    pprint(f.fetch_file_content())
    pprint(f.download())

    # SYSTEMTAGS
    pprint(nxc.get_systemtags().data)

    # TAG x FILES
    pprint(nxc.create_systemtag('TAG_NAME').data)  # in fact useless , the tag will be created automatically

    # there is bloated api for linking files
    pprint(nxc.add_systemtags_relation(
        path='/Nextcloud Manual.pdf',
        tag_name="TAG_NAME").data)
    pprint(nxc.get_systemtags_relation(path='/Nextcloud Manual.pdf').data)
    pprint(nxc.delete_systemtags_relation(
        path='/Nextcloud Manual.pdf',
        tag_name="TAG_NAME").data)

    # and a user friendly one
    f = nxc.get_file('/Nextcloud Manual.pdf')
    f.add_tag(tag_name='TAG_NAME')
    f.get_tags()
    f.remove_tag(tag_name='TAG_NAME')
    # to improve perfs you shall keep the tag ids fetched with get_systemtags

    pprint(nxc.delete_systemtag('TAG_NAME').data)

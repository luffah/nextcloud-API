# -*- coding: utf-8 -*-
import os

from .base import BaseTestCase, LocalNxcUserMixin


class TestSystemTags(LocalNxcUserMixin, BaseTestCase):

    def test_create_and_fetch_tag(self):
        _nxc = self.nxc
        tag_name = self.get_random_string(length=40) + u"¡pŷtëst!"

        tags = _nxc.get_systemtags()
        assert tag_name not in [t.display_name for t in tags]

        assert _nxc.create_systemtag(tag_name).is_ok

        tags = _nxc.get_systemtags()
        print('TestSystemTags', tags)
        assert tag_name in [t.display_name for t in tags]

        assert _nxc.delete_systemtag(tag_name).is_ok

        tags = _nxc.get_systemtags()
        assert tag_name not in [t.display_name for t in tags]


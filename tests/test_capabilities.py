# -*- coding: utf-8 -*-
from .base import BaseTestCase, NEXTCLOUD_VERSION


class TestCapabilities(BaseTestCase):

    def test_get_capabilities(self):
        res = self.nxc.get_capabilities()
        assert res.is_ok
        assert str(res.data['version']['major']) == NEXTCLOUD_VERSION

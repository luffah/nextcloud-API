# -*- coding: utf-8 -*-
from unittest import TestCase
from .base import BaseTestCase
from nextcloud.base import BaseApiWrapper
from nextcloud.requester import Requester, NextCloudConnectionError

class DummyWrapper(BaseApiWrapper):
    API_URL = '/wrong'

class TestRequester(BaseTestCase):

    def test_wrong_url(self):
        wrong_url = 'http://wrong-url.wrong'
        wrapper = DummyWrapper(self.nxc.with_attr(
            endpoint=wrong_url, json_output=False,
            user='user', password='password'
        ))
        req = Requester(wrapper)
        exception_raised = False
        try:
            req.get('')
        except NextCloudConnectionError as e:
            exception_raised = True
            assert wrong_url in str(e)
        assert exception_raised


# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from unittest import TestCase
from .base import BaseTestCase
from nextcloud.base import BaseApiWrapper
from nextcloud.session import NextCloudConnectionError

class DummyWrapper(BaseApiWrapper):
    API_URL = '/wrong'

class TestRequester(BaseTestCase):

    def test_wrong_url(self):
        wrong_url = 'http://wrong-url.wrong'
        wrapper = DummyWrapper(self.nxc.with_attr(
            endpoint=wrong_url,
            user='user',
            password='password'
        ))
        exception_raised = False
        try:
            wrapper.requester.get('')
        except NextCloudConnectionError as e:
            exception_raised = True
            assert wrong_url in str(e)
        assert exception_raised


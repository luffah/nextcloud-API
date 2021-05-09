# -*- coding: utf-8 -*-
from . import base


def test_nonsense_hostname():
    nxc = base.NextCloud("foo", "bar", "baz")
    issues = nxc.get_connection_issues()
    assert "foo" in issues


def test_nonexistent_hostname():
    nxc = base.NextCloud("http://loooooool.no-way", "bar", "baz")
    issues = nxc.get_connection_issues()
    assert "loooooool.no-way" in issues


def test_bad_password():
    nxc = base.NextCloud(
            base.NEXTCLOUD_URL,
            base.NEXTCLOUD_USERNAME, "Just Trolling")
    issues = nxc.get_connection_issues()
    assert "not logged in" in issues


def test_ok():
    nxc = base.NextCloud(
            base.NEXTCLOUD_URL,
            base.NEXTCLOUD_USERNAME, base.NEXTCLOUD_PASSWORD)
    issues = nxc.get_connection_issues()
    assert not issues

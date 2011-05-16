from leo.testing.browser import Browser
from tempfile import gettempdir

import mock
import os
import tempfile
import unittest2 as unittest


class TestBrowser(unittest.TestCase):
    """Tests for browser testing implementation."""

    def make_browser(self):
        app = mock.Mock()
        return Browser(app)

    def test_set_base_url(self):
        browser = self.make_browser()
        self.failIf(browser._base_url)
        browser.set_base_url('http://nohost/plone')
        self.assertEquals('http://nohost/plone', browser._base_url)

    def test_dump(self):
        browser = self.make_browser()
        browser._contents = '<html />'
        tmp = tempfile.mkdtemp()
        filename = os.path.join(tmp, 'testbrowser.html')
        browser.dump(filename)
        of = open(filename, 'r')
        self.assertEquals('<html />', of.readline())

#    def test_open(self):
#        browser = self.make_browser()
#        browser._base_url = base_url = 'http://nohost/plone'
#        browser.open(base_url)

    @mock.patch('leo.testing.browser.Browser.open')
    @mock.patch('leo.testing.browser.Browser.getControl')
    def test_login(self, getControl, open):
        username = 'username'
        password = 'password'
        browser = self.make_browser()
        browser.login(username, password)
        self.assertEquals(3, getControl.call_count)

    @mock.patch('leo.testing.browser.webbrowser')
    def test_start_zserver(self, webbrowser):
        browser = self.make_browser()
        browser.start_zserver()
        self.failUnless(webbrowser.get('firefox').open.called)

    @mock.patch('leo.testing.browser.webbrowser')
    def test_open_html(self, webbrowser):
        browser = self.make_browser()
        browser._contents = '<html />'
        browser.open_html()
        filename = os.path.join(gettempdir(), 'testbrowser.html')
        of = open(filename, 'r')
        self.assertEquals('<html />', of.readline())
        self.failUnless(webbrowser.get('firefox').open.called)

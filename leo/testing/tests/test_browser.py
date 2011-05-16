from tempfile import gettempdir

import mock
import os
import tempfile
import unittest2 as unittest


class TestBrowser(unittest.TestCase):
    """Tests for browser testing implementation."""

    def tearDown(self):
        filename = os.path.join(gettempdir(), 'testbrowser.html')
        if os.path.isfile(filename):
            os.remove(filename)

    def make_browser(self):
        from leo.testing.browser import Browser
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

    def test_open(self):
        browser = self.make_browser()
        browser.set_base_url('http://nohost/plone')

        browser.mech_browser.open = mock.Mock()
        browser.mech_browser.response = mock.Mock()
        browser.mech_browser.response().info.return_value = {}

        browser.open('/foo/bar')
        # Assert the underlying test browser was called with the full URL.
        browser.mech_browser.open.assert_called_with('http://nohost/plone/foo/bar', None)

    @mock.patch('leo.testing.browser.Browser.open')
    @mock.patch('leo.testing.browser.Browser.getControl')
    def test_login(self, getControl, open):
        username = 'username'
        password = 'password'
        browser = self.make_browser()
        browser.login(username, password)
        self.assertEquals(getControl.call_args_list, [
            ((), {'name': '__ac_name'}),
            ((), {'name': '__ac_password'}),
            (('Log in',), {})])

    @mock.patch('leo.testing.browser.webbrowser')
    def test_start_zserver(self, webbrowser):
        browser = self.make_browser()
        browser.start_zserver()
        webbrowser.get.assert_called_with('firefox')
        self.failUnless(webbrowser.get().open.called)

    @mock.patch('leo.testing.browser.webbrowser')
    def test_open_html(self, webbrowser):
        browser = self.make_browser()
        browser._contents = '<html />'
        browser.open_html()
        filename = os.path.join(gettempdir(), 'testbrowser.html')
        of = open(filename, 'r')
        self.assertEquals('<html />', of.readline())
        webbrowser.get.assert_called_with('firefox')
        self.failUnless(webbrowser.get().open.called)

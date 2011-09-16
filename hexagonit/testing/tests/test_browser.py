from tempfile import gettempdir

import mock
import os
import tempfile
import unittest2 as unittest


class TestBrowser(unittest.TestCase):
    """Tests for browser testing implementation."""

    def tearDown(self):
        files = ['testbrowser.html', 'some.html']
        for fil in files:
            filename = os.path.join(gettempdir(), fil)
            if os.path.isfile(filename):
                os.remove(filename)

    def make_browser(self):
        from hexagonit.testing.browser import Browser
        app = mock.Mock()
        return Browser(app)

    def test_setBaseUrl(self):
        browser = self.make_browser()
        self.failIf(browser._base_url)
        browser.setBaseUrl('http://nohost/plone')
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
        browser.setBaseUrl('http://nohost/plone')

        browser.mech_browser.open = mock.Mock()
        browser.mech_browser.response = mock.Mock()
        browser.mech_browser.response().info.return_value = {}

        browser.open('/foo/bar')
        # Assert the underlying test browser was called with the full URL.
        browser.mech_browser.open.assert_called_with('http://nohost/plone/foo/bar', None)

    def test_setHeader(self):
        browser = self.make_browser()
        browser.mech_browser.addheaders = [('User-agent', 'Python-urllib/2.6'), ('If-Modified-Since', 'Tue, 17 May 2011 08:39:06 GMT')]
        browser.setHeader('If-Modified-Since', 'Tue, 18 May 2011 00:00:07 GMT')
        self.assertEquals(
            [('User-agent', 'Python-urllib/2.6'), ('If-Modified-Since', 'Tue, 18 May 2011 00:00:07 GMT')], browser.mech_browser.addheaders)

    @mock.patch('hexagonit.testing.browser.Browser.open')
    @mock.patch('hexagonit.testing.browser.Browser.getControl')
    def test_login(self, getControl, open):
        username = 'username'
        password = 'password'
        browser = self.make_browser()
        browser.setBaseUrl('http://nohost/plone')
        browser.login(username, password)
        self.assertEquals(getControl.call_args_list, [
            ((), {'name': '__ac_name'}),
            ((), {'name': '__ac_password'}),
            (('Log in',), {})])

    @mock.patch('hexagonit.testing.browser.getUtility')
    @mock.patch('hexagonit.testing.browser.getMultiAdapter')
    def test_deletePortletManager(self, getMultiAdapter, getUtility):
        portlet_managers = {'plone.leftcolumn': '', 'plone.rightcolumn': ''}
        getMultiAdapter.return_value = portlet_managers
        browser = self.make_browser()
        portal = mock.Mock()
        name = 'plone.leftcolumn'
        browser.deletePortletManager(portal, name)
        self.assertEquals({'plone.rightcolumn': ''}, portlet_managers)

    @mock.patch('hexagonit.testing.browser.webbrowser')
    def test_openBrowser(self, webbrowser):
        browser = self.make_browser()
        browser._contents = '<html />'
        browser.openBrowser()
        filename = os.path.join(gettempdir(), 'testbrowser.html')
        of = open(filename, 'r')
        self.assertEquals('<html />', of.readline())
        self.failUnless(webbrowser.open_new_tab.called)
        ## Write html contents to some.html file.
        browser.openBrowser(filename="some.html")
        filename = os.path.join(gettempdir(), 'some.html')
        of = open(filename, 'r')
        self.assertEquals('<html />', of.readline())
        self.failUnless(webbrowser.open_new_tab.called)
        ## Open with firefox.
        browser.openBrowser('firefox')
        webbrowser.get.assert_called_with('firefox')
        self.failUnless(webbrowser.open_new_tab.called)

    def test_post_to_not_existing_page(self):
        from urllib2 import HTTPError
        browser = self.make_browser()
        browser.setBaseUrl('http://nohost/plone')
        data = [('content-type', 'text/plain'), ('filename', 'filename.txt')]
        self.assertRaises(HTTPError, lambda: browser.post('/@@no-page', data))

from tempfile import gettempdir
from leo.testing.browser import BOUNDARY

import mock
import os
import tempfile
import unittest2 as unittest
import StringIO


VALUE = [
    {
        'data': StringIO.StringIO('text_file'),
        'content-type': 'text/plain',
        'filename': 'filename.txt'},
    {
        'data': StringIO.StringIO('image_file'),
        'content-type': 'image/gif',
        'filename': 'filename.png'}]


class TestBrowser(unittest.TestCase):
    """Tests for browser testing implementation."""

    def setUp(self):
        self.parts = '\r\n'.join([
            '--BBBBB',
            'Content-Disposition: file; filename="filename.txt"',
            'Content-Type: text/plain',
            '',
            'text_file',
            '--BBBBB',
            'Content-Disposition: file; filename="filename.png"',
            'Content-Type: image/gif',
            '',
            'image_file',
            '--BBBBB--'])

    def tearDown(self):
        filename = os.path.join(gettempdir(), 'testbrowser.html')
        if os.path.isfile(filename):
            os.remove(filename)

    def make_browser(self):
        from leo.testing.browser import Browser
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

    @mock.patch('leo.testing.browser.getUtility')
    @mock.patch('leo.testing.browser.getMultiAdapter')
    def test_deletePortletManager(self, getMultiAdapter, getUtility):
        portlet_managers = {'plone.leftcolumn': '', 'plone.rightcolumn': ''}
        getMultiAdapter.return_value = portlet_managers
        browser = self.make_browser()
        portal = mock.Mock()
        name = 'plone.leftcolumn'
        browser.deletePortletManager(portal, name)
        self.assertEquals({'plone.rightcolumn': ''}, portlet_managers)

    @mock.patch('leo.testing.browser.webbrowser')
    def test_startZserver(self, webbrowser):
        browser = self.make_browser()
        browser.startZserver()
        self.failUnless(webbrowser.open_new_tab.called)

    @mock.patch('leo.testing.browser.webbrowser')
    def test_openBrowser(self, webbrowser):
        browser = self.make_browser()
        browser._contents = '<html />'
        browser.openBrowser()
        filename = os.path.join(gettempdir(), 'testbrowser.html')
        of = open(filename, 'r')
        self.assertEquals('<html />', of.readline())
        self.failUnless(webbrowser.open_new_tab.called)

    def test_post(self):
        url = 'http://localhost/@@echo.html'
        data = 'x=1&y=2'
        browser = self.make_browser()
        from urllib2 import HTTPError
        browser.setBaseUrl('http://nohost/plone')

    def test_files(self):
        from leo.testing.browser import files
        value = VALUE
        self.assertEquals(self.parts, files(value))

    def test_multifile(self):
        from leo.testing.browser import multifile
        key = 'files'
#        boundary = 'BOUNDARY'
        boundary = BOUNDARY
        value = VALUE
#        parts = [
#            '--BOUNDARY',
#            'Content-Disposition: form-data; name="files"',
#            'Content-Type: multipart/mixed; boundary=BBBBB',
#            '',
#            self.parts,
#            '']
        res = [
#            '--BOUNDARY',
            '--{0}'.format(BOUNDARY),
            'Content-Disposition: form-data; name="files"',
            'Content-Type: multipart/mixed; boundary=BBBBB',
            '',
            '--BBBBB\r\nContent-Disposition: file; filename="filename.txt"\r\nContent-Type: text/plain\r\n\r\ntext_file\r\n--BBBBB\r\nContent-Disposition: file; filename="filename.png"\r\nContent-Type: image/gif\r\n\r\nimage_file\r\n--BBBBB--',
            '']
        self.assertEquals(res, multifile(key, value, boundary))

    def test_non_file_single_field_multipart_formdata(self):
        browser = self.make_browser()
        fields = {'username': 'Some Name'}
        res = (
            '--{0}\r\nContent-Disposition: form-data; name=username\r\nContent-Length: 9\r\n\r\nSome Name\r\n--{0}--\r\n'.format(BOUNDARY),
            'multipart/form-data; boundary={0}'.format(BOUNDARY))
        self.assertEquals(res, browser.multipart_formdata(fields))

    def test_none_file_multi_fields_multipart_formdata(self):
        browser = self.make_browser()
        fields = {
            'username': 'Some Name',
            'userpass': 'Some Pass'}
        res = (
            '--{0}\r\nContent-Disposition: form-data; name=username\r\nContent-Length: 9\r\n\r\nSome Name\r\n--{0}\r\nContent-Disposition: form-data; name=userpass\r\nContent-Length: 9\r\n\r\nSome Pass\r\n--{0}--\r\n'.format(BOUNDARY),
             'multipart/form-data; boundary={0}'.format(BOUNDARY))
        self.assertEquals(res, browser.multipart_formdata(fields))

    def test_single_file_multipart_formdata(self):
        browser = self.make_browser()
        fields = {
            'files': {
                'data': StringIO.StringIO('text_file'),
                'content-type': 'text/plain',
                'filename': 'filename.txt'}}
        res = (
            '--{0}\r\nContent-Disposition: form-data; name=files; filename=filename.txt\r\nContent-Type: text/plain\r\n\r\ntext_file\r\n--{0}--\r\n'.format(BOUNDARY),
            'multipart/form-data; boundary={0}'.format(BOUNDARY))
        self.assertEquals(res, browser.multipart_formdata(fields))

    def test_multiple_file_multipart_formdata(self):
        browser = self.make_browser()
        fields = {
            'files': [
                {
                    'data': StringIO.StringIO('text_file'),
                    'content-type': 'text/plain',
                    'filename': 'filename.txt'},
                {
                    'data': StringIO.StringIO('image_file'),
                    'content-type': 'image/gif',
                    'filename': 'filename.png'}]}
        res = (
            '--{0}\r\nContent-Disposition: form-data; name="files"\r\nContent-Type: multipart/mixed; boundary=BBBBB\r\n\r\n--BBBBB\r\nContent-Disposition: file; filename="filename.txt"\r\nContent-Type: text/plain\r\n\r\ntext_file\r\n--BBBBB\r\nContent-Disposition: file; filename="filename.png"\r\nContent-Type: image/gif\r\n\r\nimage_file\r\n--BBBBB--\r\n--{0}--\r\n'.format(BOUNDARY),
            'multipart/form-data; boundary={0}'.format(BOUNDARY))
        self.assertEquals(res, browser.multipart_formdata(fields))

    def test_non_file_field_single_file_field_and_multiple_file_field_together(self):
        browser = self.make_browser()
        fields = {
            'username': 'Some Name',
            'single_file': {
                'data': StringIO.StringIO('single_text_file'),
                'content-type': 'text/plain',
                'filename': 'single_filename.txt'},
            'multiple_files': [
                {
                    'data': StringIO.StringIO('text_file'),
                    'content-type': 'text/plain',
                    'filename': 'filename.txt'},
                {
                    'data': StringIO.StringIO('image_file'),
                    'content-type': 'image/gif',
                    'filename': 'filename.png'}]}
        res = (
            '--{0}\r\nContent-Disposition: form-data; name="multiple_files"\r\nContent-Type: multipart/mixed; boundary=BBBBB\r\n\r\n--BBBBB\r\nContent-Disposition: file; filename="filename.txt"\r\nContent-Type: text/plain\r\n\r\ntext_file\r\n--BBBBB\r\nContent-Disposition: file; filename="filename.png"\r\nContent-Type: image/gif\r\n\r\nimage_file\r\n--BBBBB--\r\n--{0}\r\nContent-Disposition: form-data; name=single_file; filename=single_filename.txt\r\nContent-Type: text/plain\r\n\r\nsingle_text_file\r\n--{0}\r\nContent-Disposition: form-data; name=username\r\nContent-Length: 9\r\n\r\nSome Name\r\n--{0}--\r\n'.format(BOUNDARY),
            'multipart/form-data; boundary={0}'.format(BOUNDARY))
        self.assertEquals(res, browser.multipart_formdata(fields))


class TestLeoMechanizeBrowser(unittest.TestCase):
    """Tests for mechanize browser testing implementation."""

    def test_httpHandlerFactory(self):
        from leo.testing.browser import LeoMechanizeBrowser
        from leo.testing.browser import LeoHTTPHandler
        app = mock.Mock()
        mech_browser = LeoMechanizeBrowser(app)
        self.failUnless(isinstance(mech_browser.handler_classes['http'](), LeoHTTPHandler))


class TestLeoHTTPHandler(unittest.TestCase):
    """Tests for http handler testing implementation."""

    def test_do_request(self):
        from leo.testing.browser import LeoHTTPHandler
#        from leo.testing.browser import BOUNDARY
        from mechanize._request import Request
        request = Request('/plone/@@echo', data=True)
        request.get_host = mock.Mock()
        request.get_host.return_value = 'nohost'
        request.has_data = mock.Mock()
        request.has_data.return_value = True
        request.get_data = mock.Mock()
        request.get_data.return_value = 'Data'
        request.has_header = mock.Mock()
        request.has_header.return_value = False
        request.has_proxy = mock.Mock()
        request.has_proxy.return_value = False
        app = mock.Mock()
        handler = LeoHTTPHandler(app)
        handler.parent = mock.Mock()
        handler.parent.addheaders = [('User-agent', 'Python-urllib/2.6')]
        handler.do_request_(request)
        ctype = 'multipart/form-data; boundary={0}'.format(BOUNDARY)
        self.assertEquals(ctype, request.unredirected_hdrs['Content-type'])

    def test_http_request(self):
        """Testing that http_request is the same as do_request_ method."""
        from leo.testing.browser import LeoHTTPHandler
        app = mock.Mock()
        handler = LeoHTTPHandler(app)
        self.assertEquals('do_request_', handler.http_request.im_func.__name__)
        self.assertEquals('LeoHTTPHandler', handler.http_request.im_class.__name__)

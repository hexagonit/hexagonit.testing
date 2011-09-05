import mock
import unittest2 as unittest


class TestLeoHTTPHandler(unittest.TestCase):
    """Tests for http handler testing implementation."""

    def test_has_data_do_request(self):
        from leo.testing.mech import LeoHTTPHandler
        from leo.testing.mime import BOUNDARY
        from mechanize._request import Request
        request = Request('/plone/@@echo', data=True)
        request.get_host = mock.Mock()
        request.get_host.return_value = 'nohost'
        request.has_data = mock.Mock()
        request.has_data.return_value = True
        request.get_data = mock.Mock()
        request.get_data.return_value = 'Data'
        request.has_proxy = mock.Mock()
        request.has_proxy.return_value = False
        app = mock.Mock()
        handler = LeoHTTPHandler(app)
        handler.parent = mock.Mock()
        handler.parent.addheaders = [('User-agent', 'Python-urllib/2.6')]
        handler.do_request_(request)
        ctype = 'multipart/form-data; boundary={0}'.format(BOUNDARY)
        self.assertEquals(ctype, request.unredirected_hdrs['Content-type'])

    def test_has_not_data_do_request(self):
        from leo.testing.mech import LeoHTTPHandler
        from mechanize._request import Request
        request = Request('/plone/@@echo', data=True)
        request.get_host = mock.Mock()
        request.get_host.return_value = 'nohost'
        request.has_data = mock.Mock()
        request.has_data.return_value = False
        request.has_proxy = mock.Mock()
        request.has_proxy.return_value = False
        app = mock.Mock()
        handler = LeoHTTPHandler(app)
        handler.parent = mock.Mock()
        handler.parent.addheaders = [('User-agent', 'Python-urllib/2.6')]
        handler.do_request_(request)
#        ctype = 'multipart/form-data; boundary={0}'.format(BOUNDARY)
        ## Now uses default application/x-www-form-urlencoded istead of multipart/form-data
        self.assertRaises(KeyError, lambda: request.unredirected_hdrs['Content-type'])

    def test_http_request(self):
        """Testing that http_request is the same as do_request_ method."""
        from leo.testing.mech import LeoHTTPHandler
        app = mock.Mock()
        handler = LeoHTTPHandler(app)
        self.assertEquals('do_request_', handler.http_request.im_func.__name__)
        self.assertEquals('LeoHTTPHandler', handler.http_request.im_class.__name__)


class TestLeoMechanizeBrowser(unittest.TestCase):
    """Tests for mechanize browser testing implementation."""

    def test_httpHandlerFactory(self):
        from leo.testing.mech import LeoMechanizeBrowser
        from leo.testing.mech import LeoHTTPHandler
        app = mock.Mock()
        mech_browser = LeoMechanizeBrowser(app)
        self.failUnless(isinstance(mech_browser.handler_classes['http'](), LeoHTTPHandler))

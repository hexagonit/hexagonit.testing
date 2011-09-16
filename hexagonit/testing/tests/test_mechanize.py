import mock
import unittest2 as unittest


class TestHexagonitHTTPHandler(unittest.TestCase):
    """Tests for http handler testing implementation."""

    def test_has_data_do_request(self):
        from hexagonit.testing.mech import HexagonitHTTPHandler
        from hexagonit.testing.mime import BOUNDARY
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
        handler = HexagonitHTTPHandler(app)
        handler.parent = mock.Mock()
        handler.parent.addheaders = [('User-agent', 'Python-urllib/2.6')]
        handler.do_request_(request)
        ctype = 'multipart/form-data; boundary={0}'.format(BOUNDARY)
        self.assertEquals(ctype, request.unredirected_hdrs['Content-type'])

    def test_has_not_data_do_request(self):
        from hexagonit.testing.mech import HexagonitHTTPHandler
        from mechanize._request import Request
        request = Request('/plone/@@echo', data=True)
        request.get_host = mock.Mock()
        request.get_host.return_value = 'nohost'
        request.has_data = mock.Mock()
        request.has_data.return_value = False
        request.has_proxy = mock.Mock()
        request.has_proxy.return_value = False
        app = mock.Mock()
        handler = HexagonitHTTPHandler(app)
        handler.parent = mock.Mock()
        handler.parent.addheaders = [('User-agent', 'Python-urllib/2.6')]
        handler.do_request_(request)
#        ctype = 'multipart/form-data; boundary={0}'.format(BOUNDARY)
        ## Now uses default application/x-www-form-urlencoded istead of multipart/form-data
        self.assertRaises(KeyError, lambda: request.unredirected_hdrs['Content-type'])

    def test_http_request(self):
        """Testing that http_request is the same as do_request_ method."""
        from hexagonit.testing.mech import HexagonitHTTPHandler
        app = mock.Mock()
        handler = HexagonitHTTPHandler(app)
        self.assertEquals('do_request_', handler.http_request.im_func.__name__)
        self.assertEquals('HexagonitHTTPHandler', handler.http_request.im_class.__name__)


class TestHexagonitMechanizeBrowser(unittest.TestCase):
    """Tests for mechanize browser testing implementation."""

    def test_httpHandlerFactory(self):
        from hexagonit.testing.mech import HexagonitMechanizeBrowser
        from hexagonit.testing.mech import HexagonitHTTPHandler
        app = mock.Mock()
        mech_browser = HexagonitMechanizeBrowser(app)
        self.failUnless(isinstance(mech_browser.handler_classes['http'](), HexagonitHTTPHandler))

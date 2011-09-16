from hexagonit.testing.mime import BOUNDARY
from plone.testing._z2_testbrowser import Zope2HTTPHandler
from plone.testing._z2_testbrowser import Zope2MechanizeBrowser

import urllib2


class HexagonitHTTPHandler(Zope2HTTPHandler):
    """HTTPHandler which makes POST method work for <form />s."""

    def do_request_(self, request):
        host = request.get_host()
        if not host:
            raise urllib2.URLError('no host given')

        if request.has_data():  # POST
            data = request.get_data()
            if not request.has_header('Content-type'):
                request.add_unredirected_header(
                    'Content-type',
                    'multipart/form-data; boundary={0}'.format(BOUNDARY))
            if not request.has_header('Content-length'):
                request.add_unredirected_header(
                    'Content-length', '{0}'.format(len(data)))
        return Zope2HTTPHandler.do_request_(self, request)

    http_request = do_request_


class HexagonitMechanizeBrowser(Zope2MechanizeBrowser):
    """MechanizeBrowser which makes POST method work for <form />s."""

    def __init__(self, app, *args, **kws):
        import mechanize

        ## We need HexagonitHTTPHandler here to make POST method work for <form />s.
        def httpHandlerFactory():
            return HexagonitHTTPHandler(app)

        self.handler_classes = mechanize.Browser.handler_classes.copy()
        self.handler_classes["http"] = httpHandlerFactory
        self.default_others = [cls for cls in self.default_others
                               if cls in mechanize.Browser.handler_classes]
        mechanize.Browser.__init__(self, *args, **kws)

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.testing import z2
from tempfile import gettempdir
from Testing.ZopeTestCase.utils import startZServer
from zope.component import getMultiAdapter
from zope.component import getUtility
from plone.testing._z2_testbrowser import Zope2MechanizeBrowser
from plone.testing._z2_testbrowser import Zope2HTTPHandler
from urllib2 import URLError
from urllib2 import splittype
from urllib2 import splithost


import mechanize
import os
import webbrowser


class Browser(z2.Browser):
    """Enhanced test browser."""

    _base_url = None

#    def __init__(self, app, url=None):
#        super(z2.Browser, self).__init__(url=url, mech_browser=LeoMechanizeBrowser(app))

    def setBaseUrl(self, base_url):
        """Sets a base URL for all subsequent requests."""
        self._base_url = base_url

    def dump(self, filename):
        """Dumps the browser contents to the given file."""
        fh = open(filename, 'w')
        fh.write(self.contents)
        fh.close()

    def open(self, url, data=None):
        """Add support for absolute paths without the base component"""
        if self._base_url is not None and url.startswith('/'):
            url = '{0}{1}'.format(self._base_url, url)

        super(self.__class__, self).open(url, data)

    def setHeader(self, name, value):
        """Set a request header possibly overwriting an existing header with
        the same name.
        """
        headers = dict((k.lower(), (k, v)) for k, v in self.mech_browser.addheaders)
        headers[name.lower()] = (name, value)
        self.mech_browser.addheaders = [headers.pop(k.lower()) for k, v in self.mech_browser.addheaders] + headers.values()

    def login(self, username, password, login_url='/login_form'):
        """Logs into the portal."""
        self.open(login_url)
        self.getControl(name='__ac_name').value = username
        self.getControl(name='__ac_password').value = password
        self.getControl('Log in').click()

    def deletePortletManager(self, portal, name):
        """Delete portlet manager of the name."""
        column = getUtility(IPortletManager, name=name)
        assignable = getMultiAdapter((portal, column), IPortletAssignmentMapping)
        del assignable[name]

    def startZserver(self, web_browser_name='firefox'):
        """Start ZServer so we can inspect site state with a normal browser
        like FireFox."""
        echo = startZServer()
        webbrowser.get(web_browser_name).open('http://%s:%s/plone' % echo)

    def openBrowser(self, web_browser_name='firefox'):
        """Dumps self.browser.contents (HTML) to a file and opens it with
        a normal browser."""
        tmp_filename = 'testbrowser.html'
        filepath = os.path.join(gettempdir(), tmp_filename)
        with open(filepath, 'w') as file:
            file.write(self.contents)
        webbrowser.get(web_browser_name).open('file://' + filepath)

#    def post(self, url, data):
#        _z2_testbrowser.Zope2HTTPHandler = LeoHTTPHandler
#        return super(Browser, self).post(url, data)


class LeoMechanizeBrowser(Zope2MechanizeBrowser):

#    def __init__(self, app, *args, **kws):
#        super(LeoMechanizeBrowser, self).__init__(app, *args, **kws)
#        def httpHandlerFactory():
#            return LeoHTTPHandler(app)
#        self.handler_classes["http"] = httpHandlerFactory


    def __init__(self, app, *args, **kws):
        def httpHandlerFactory():
            return LeoHTTPHandler(app)
        self.handler_classes = mechanize.Browser.handler_classes.copy()
        self.handler_classes["http"] = httpHandlerFactory
        self.default_others = [cls for cls in self.default_others 
                               if cls in mechanize.Browser.handler_classes]
        mechanize.Browser.__init__(self, *args, **kws)


class DoRequest(Zope2HTTPHandler):

    def do_request_(self, request):
        host = request.get_host()
        if not host:
            raise URLError('no host given')

        if request.has_data():  # POST
            data = request.get_data()
            if not request.has_header('Content-type'):
                request.add_unredirected_header(
                    'Content-type',
                    'multipart/form-data')
            if not request.has_header('Content-length'):
                request.add_unredirected_header(
                    'Content-length', '%d' % len(data))

        sel_host = host
        if request.has_proxy():
            scheme, sel = splittype(request.get_selector())
            sel_host, sel_path = splithost(sel)

        if not request.has_header('Host'):
            request.add_unredirected_header('Host', sel_host)
        for name, value in self.parent.addheaders:
            name = name.capitalize()
            if not request.has_header(name):
                request.add_unredirected_header(name, value)

        return request

class LeoHTTPHandler(DoRequest):

#    def http_open(self, req):
#        import pdb; pdb.set_trace()

#    def do_request_(self, request):
#        import pdb; pdb.set_trace()
#        pass

#    def http_request(self, request):
#        if not request.has_header('Content-type'):
#            request.add_unredirected_header(
#                'Content-type',
#                'multipart/form-data')
#        self.do_request_(request)

    http_request = DoRequest.do_request_

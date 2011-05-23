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
from mechanize import _sockettimeout
from mechanize import _rfc3986
from mechanize._mechanize import BrowserStateError
from mechanize._useragent import UserAgentBase
from mechanize import _response
from mechanize import _urllib2_fork
from mechanize._opener import OpenerDirector

import copy
import mechanize
import mimetools
import os
import urllib2
import webbrowser


MULTIPART_TEXT_TMPL = '\r\n'.join([
'--%(boundary)s',
'Content-Disposition: form-data; name=%(name)s',
'Content-Length: %(length)s',
'',
'%(value)s',
''])

MULTIPART_ONE_FILE_TMPL = '\r\n'.join([
'--%(boundary)s',
'Content-Disposition: form-data; name=%(name)s; filename=%(filename)s',
'Content-Type: %(content-type)s',
'',
'%(value)s',
''])


#def safe_utf8(s, encoding=('utf-8', 'iso-8859-15'), convert=True):
#    """Convert to utf8 if not yet string or None"""
#    value = safe_unicode(s, encoding=encoding, convert=convert)
#    if isinstance(value, unicode):
#        value = value.encode('utf-8')


class Browser(z2.Browser):
    """Enhanced test browser."""

    _base_url = None

    def __init__(self, app, url=None):
        super(z2.Browser, self).__init__(url=url, mech_browser=LeoMechanizeBrowser(app))

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

    def post(self, url, data):
        """Posting to url with multipart/form-data instead of application/x-www-form-urlencoded
        
        :param url: where data will be posted.
        :type url: str
        
        :param data: data to be posted.
        :type data: str or dict
        """
        if isinstance(data, dict):
            mf = self.multipart_formdata(data)
            data = "Content-Type: {0}\r\n\r\n{1}".format(mf[1], mf[0])
        return super(Browser, self).post(url, data)

    def multipart_formdata(self, fields):
        """
        Given a dictionary field parameters, returns the HTTP request body and the
        content_type (which includes the boundary string), to be used with an
        httplib-like call.

        This function is adapted from

           http://urllib3.googlecode.com/svn/trunk/urllib3/filepost.py
        """
        BOUNDARY = 'BOUNDARY'

        body = []
        for key, value in sorted(fields.items()):
            if isinstance(value, dict):
                body.append(MULTIPART_ONE_FILE_TMPL % {
                    'boundary' : BOUNDARY,
                    'name' : key,
                    'filename' : value['filename'],
                    'content-type' : value['content-type'],
                    'value' : value['data'].read(),
#                    'length' : len(value),
                })
            else:
                body.append(MULTIPART_TEXT_TMPL % {
                    'boundary' : BOUNDARY,
    #                'name' : safe_utf8(key),
    #                'value' : safe_utf8(value),
    #                'length' : len(safe_utf8(value)),
                    'name' : key,
                    'value' : value,
                    'length' : len(value),
                })
        body.append('--%s--\r\n' % BOUNDARY)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY

        return ''.join(body), content_type


class LeoMechanizeBrowser(Zope2MechanizeBrowser):

    def __init__(self, app, *args, **kws):
        def httpHandlerFactory():
            return LeoHTTPHandler(app)
        self.handler_classes = mechanize.Browser.handler_classes.copy()
        self.handler_classes["http"] = httpHandlerFactory
        self.default_others = [cls for cls in self.default_others 
                               if cls in mechanize.Browser.handler_classes]
        mechanize.Browser.__init__(self, *args, **kws)


    def _mech_open(self, url, data=None, update_history=True, visit=None,
                   timeout=_sockettimeout._GLOBAL_DEFAULT_TIMEOUT):
        try:
            url.get_full_url
        except AttributeError:
            # string URL -- convert to absolute URL if required
            scheme, authority = _rfc3986.urlsplit(url)[:2]
            if scheme is None:
                # relative URL
                if self._response is None:
                    raise BrowserStateError(
                        "can't fetch relative reference: "
                        "not viewing any document")
                url = _rfc3986.urljoin(self._response.geturl(), url)

        request = self._request(url, data, visit, timeout)
        visit = request.visit
        if visit is None:
            visit = True

        if visit:
            self._visit_request(request, update_history)

        success = True

        try:
#            response = UserAgentBase.open(self, request, data)
#            response = LeoUserAgent.open(self, request, data)
            fullurl = request
            timeout = _sockettimeout._GLOBAL_DEFAULT_TIMEOUT
            req = self._request(fullurl, data, None, timeout)
            req_scheme = req.get_type()
            self._maybe_reindex_handlers()
            
            
            request_processors = set(self.process_request.get(req_scheme, []))
            request_processors.update(self._any_request)
            request_processors = list(request_processors)
            request_processors.sort()
            for processor in request_processors:
                for meth_name in ["any_request", req_scheme+"_request"]:
                    meth = getattr(processor, meth_name, None)
                    if meth:
                        req = meth(req)

            # In Python >= 2.4, .open() supports processors already, so we must
            # call ._open() instead.
            urlopen = _urllib2_fork.OpenerDirector._open
            response = urlopen(self, req, data)

            # post-process response
            response_processors = set(self.process_response.get(req_scheme, []))
            response_processors.update(self._any_response)
            response_processors = list(response_processors)
            response_processors.sort()
            for processor in response_processors:
                for meth_name in ["any_response", req_scheme+"_response"]:
                    meth = getattr(processor, meth_name, None)
                    if meth:
                        response = meth(req, response)
        except urllib2.HTTPError, error:
            success = False
            if error.fp is None:  # not a response
                raise
            response = error
##         except (IOError, socket.error, OSError), error:
##             # Yes, urllib2 really does raise all these :-((
##             # See test_urllib2.py for examples of socket.gaierror and OSError,
##             # plus note that FTPHandler raises IOError.
##             # XXX I don't seem to have an example of exactly socket.error being
##             #  raised, only socket.gaierror...
##             # I don't want to start fixing these here, though, since this is a
##             # subclass of OpenerDirector, and it would break old code.  Even in
##             # Python core, a fix would need some backwards-compat. hack to be
##             # acceptable.
##             raise

        if visit:
            self._set_response(response, False)
            response = copy.copy(self._response)
        elif response is not None:
            response = _response.upgrade_response(response)

        if not success:
            raise response
        return response



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
                    'multipart/form-data; boundary=BOUNDARY')
#                    'application/x-www-form-urlencoded')
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

    http_request = DoRequest.do_request_


#class LeoUserAgent(UserAgentBase):
##class LeoUserAgent(OpenerDirector):
#    pass

##    def open(self, fullurl, data=None,
##             timeout=_sockettimeout._GLOBAL_DEFAULT_TIMEOUT):
##        req = self._request(fullurl, data, None, timeout)
##        req_scheme = req.get_type()

##        self._maybe_reindex_handlers()

##        # pre-process request
##        # XXX should we allow a Processor to change the URL scheme
##        #   of the request?
##        request_processors = set(self.process_request.get(req_scheme, []))
##        request_processors.update(self._any_request)
##        request_processors = list(request_processors)
##        request_processors.sort()
##        for processor in request_processors:
##            for meth_name in ["any_request", req_scheme+"_request"]:
##                meth = getattr(processor, meth_name, None)
##                if meth:
##                    req = meth(req)

##        # In Python >= 2.4, .open() supports processors already, so we must
##        # call ._open() instead.
##        urlopen = _urllib2_fork.OpenerDirector._open
##        response = urlopen(self, req, data)

##        # post-process response
##        response_processors = set(self.process_response.get(req_scheme, []))
##        response_processors.update(self._any_response)
##        response_processors = list(response_processors)
##        response_processors.sort()
##        for processor in response_processors:
##            for meth_name in ["any_response", req_scheme+"_response"]:
##                meth = getattr(processor, meth_name, None)
##                if meth:
##                    response = meth(req, response)

##        return response

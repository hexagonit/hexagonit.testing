from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.testing import z2
from plone.testing._z2_testbrowser import Zope2HTTPHandler
from plone.testing._z2_testbrowser import Zope2MechanizeBrowser
from tempfile import gettempdir
from Testing.ZopeTestCase.utils import startZServer
from urllib2 import splithost
from urllib2 import splittype
from urllib2 import URLError
from zope.component import getMultiAdapter
from zope.component import getUtility

import mechanize
import os
import webbrowser
import hashlib


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


MULTIPART_MULTI_FILE_TMPL = '\r\n'.join([
'--%(boundary)s',
'Content-Disposition: form-data; name=%(name)s; filename=%(filename)s',
'Content-Type: multipart/mixed; boundary=BBBBB'
'',
'%(value)s',
''])


FILES = """--BBBBB
Content-Disposition: file; filename="file1.txt"
Content-Type: text/plain

Some text comes here.
"""

boundary = 'BOUNDARY'
m = hashlib.md5()
m.update(boundary)


BOUNDARY = m.hexdigest()
#BOUNDARY = 'BOUNDARY'


def files(value):
    body = []
    for val in value:
        data = val['data']
        data.seek(0)
        parts = [
            '--BBBBB',
            'Content-Disposition: file; filename="{0}"'.format(val['filename']),
            'Content-Type: {0}'.format(val['content-type']),
            '',
            '{0}'.format(data.read())]
        body.append('\r\n'.join(parts))
    body = '\r\n'.join(body) + '\r\n--BBBBB--'
    return body


def multifile(key, value, boundary):
    values = files(value)
    parts = [
        '--{0}'.format(boundary),
        'Content-Disposition: form-data; name="{0}"'.format(key),
        'Content-Type: multipart/mixed; boundary=BBBBB',
        '',
        values,
        '']
    return parts


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
        webbrowser.open_new_tab('http://%s:%s/plone' % echo)

    def openBrowser(self, web_browser_name='firefox'):
        """Dumps self.browser.contents (HTML) to a file and opens it with
        a normal browser."""
        tmp_filename = 'testbrowser.html'
        filepath = os.path.join(gettempdir(), tmp_filename)
        with open(filepath, 'w') as file:
            file.write(self.contents)
        webbrowser.open_new_tab('file://' + filepath)

    def DISABLED_post(self, url, data):
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
#        BOUNDARY = 'BOUNDARY'

        body = []
        for key, value in sorted(fields.items()):
            if isinstance(value, dict):
                body.append(MULTIPART_ONE_FILE_TMPL % {
                    'boundary': BOUNDARY,
                    'name': key,
                    'filename': value['filename'],
                    'content-type': value['content-type'],
                    'value': value['data'].read(),
                })
            elif isinstance(value, list):
                body.append('\r\n'.join(multifile(key, value, BOUNDARY)))
            else:
                body.append(MULTIPART_TEXT_TMPL % {
                    'boundary': BOUNDARY,
                    'name': key,
                    'value': value,
                    'length': len(value),
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


class LeoHTTPHandler(Zope2HTTPHandler):

    def do_request_(self, request):
        Zope2HTTPHandler.do_request_(self, request)
        request.add_unredirected_header(
            'Content-type',
            'multipart/form-data; boundary={0}'.format(BOUNDARY))

        return request

    http_request = do_request_

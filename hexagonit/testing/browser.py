from hexagonit.testing.mech import HexagonitMechanizeBrowser
from hexagonit.testing.mime import multipart_formdata
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.testing import z2
from tempfile import gettempdir
# from Testing.ZopeTestCase.utils import startZServer
from zope.component import getMultiAdapter
from zope.component import getUtility

import os
import webbrowser


class Browser(z2.Browser):
    """Enhanced test browser."""

    _base_url = None

    def __init__(self, app, url=None):
        """Use __init__ method from the super class,
        but pass HexagonitMechanizeBrowser instance to mech_browser to use
        POST method for <form />s instead of GET method.

        :param app: Application object.
        :type app: object

        :param url: URL.
        :type url: str
        """
        super(z2.Browser, self).__init__(url=url, mech_browser=HexagonitMechanizeBrowser(app))

    def setBaseUrl(self, base_url):
        """Sets a base URL for all subsequent requests.

        Usually the base URL is set to ``portal_url`` at the beginning of the
        test with main benefit that subsequent calls to ``browser.open``
        are easier to read. So instead of writing:

            >>> browser.open('{0}/path/to/object'.format(self.portal.absolute_url()))
            >>> browser.open('{0}/path/to/somewhere/else'.format(self.portal.absolute_url()))

        You can write:

            >>> browser.setBaseUrl(self.portal.absolute_url())
            >>> browser.open('/path/to/object')
            >>> browser.open('/path/to/somewhere/else')

        :param base_url: Base URL to use in subsequent calls to ``open``.
        :type base_url: str
        """
        self._base_url = base_url

    def dump(self, filename):
        """Dumps the browser contents to the given file.

        :param filename: File name.
        :type filename: str
        """
        with open(filename, 'w') as fh:
            fh.write(self.contents)

    def open(self, url, data=None):
        """Opens the given URL in the test browser with additional support for
        base URLs (set using :py:meth:`hexagonit.testing.browser.Browser.setBaseUrl`).

        The base URL is used when the given URL is an absolute path.

        :param url: Absolute path or full URL.
        :type url: str

        :param data: Request Data.
        :type data: dict
        """
        if self._base_url is not None and url.startswith('/'):
            url = '{0}{1}'.format(self._base_url, url)

        super(self.__class__, self).open(url, data)

    def setHeader(self, name, value):
        """Sets a request header possibly overwriting an existing header with
        the same name.

        :param name: Header name.
        :type name: str

        :param value: Header value against the name.
        :type value: str
        """
        headers = dict((k.lower(), (k, v)) for k, v in self.mech_browser.addheaders)
        headers[name.lower()] = (name, value)
        self.mech_browser.addheaders = [headers.pop(k.lower()) for k, v in self.mech_browser.addheaders] + headers.values()

    def login(self, username, password, login_url='/login_form'):
        """Logs into the portal.

        Assumes that the browser has been configured with a base URL pointing
        to the portal root (see :py:meth:`hexagonit.testing.browser.Browser.setBaseUrl`).

        :param username: User name.
        :type username: str

        :param password: Password.
        :type password: str

        :param login_url: Absolute path for the login URL.
        :type login_url: str
        """
        self.open(login_url)
        self.getControl(name='__ac_name').value = username
        self.getControl(name='__ac_password').value = password
        self.getControl('Log in').click()

    def deletePortletManager(self, portal, name):
        """Deletes a portlet manager of the given name.

        Usually it is u'plone.leftcolumn' or u'plone.rightcolumn'.

        :param portal: Portal object.
        :type portal: object

        :param name: Portlet manager name.
        :type name: unicode
        """
        column = getUtility(IPortletManager, name=name)
        assignable = getMultiAdapter((portal, column), IPortletAssignmentMapping)
        del assignable[name]

     ## This method is not working properly for now.
#    def startZserver(self, browser=None):
#        """Start ZServer so we can inspect site state with a normal browser
#        like FireFox.
#        If browser is not specified, system default browser will be used.

#        :param browser: Excutable browser name such as 'firefox'.
#        :type browser: str
#        """
#        host, port = startZServer()
#        url = 'http://{0}:{1}/plone'.format(host, port)
#        wbrowser = webbrowser if browser is None else webbrowser.get(browser)
#        wbrowser.open_new_tab(url)

    def openBrowser(self, browser=None, filename='testbrowser.html'):
        """Dumps self.browser.contents (HTML) to a file and opens it with
        a normal browser.

        If browser is not specified, system default browser will be used.

        :param browser: Excutable browser name such as 'firefox'.
        :type browser: str

        :param filename: HTML file name where the results of html contents will be writen.
        :type filename: str
        """
        filepath = os.path.join(gettempdir(), filename)
        with open(filepath, 'w') as fh:
            fh.write(self.contents)

        wbrowser = webbrowser if browser is None else webbrowser.get(browser)
        wbrowser.open_new_tab('file://' + filepath)

    def post(self, url, data):
        """Posts the given data to the given url with a ``multipart/form-data``
        submission instead of ``application/x-www-form-urlencoded``.

        This is particularly useful if you need to test web APIs which expect
        POST request without having to generate forms just for testing purposes.

            >>> browser.post('/web-api', {
            ...   'foo': 'bar',
            ...   'bar': 'foo',
            ... })

        To POST a file you can use the following dictionary structure as value for
        the field:

        .. code-block:: python

            { 'filename': 'my-document.pdf',
              'content-type': 'application/pdf',
              'data' : open('/tmp/my-document.pdf'),
              }

        The dictionary must contain the above fields where ``filename`` and ``content-type``
        are strings and ``data`` is a file-like object. To perform a file upload you could
        make a following kind of call:

            >>> browser.post('/web-api', {
            ...   'my_file_field': {
            ...       'filename': 'my-document.pdf',
            ...       'content-type': 'application/pdf',
            ...       'data' : open('/tmp/my-document.pdf'),
            ...       }
            ... })

        If the order of the submitted fields is significant a sequence of
        ``(key, value)`` tuples may be used instead.

            >>> browser.post('/web-api', [
            ...   ('foo', 'bar'),
            ...   ('bar', 'foo'),
            ... ])

        :param url: where data will be posted.
        :type url: str

        :param data: Submission data either as an iterable of ``(key, value)``
            tuples or a dictionary.
        :type data: iterable or dict
        """
        body, content_type = multipart_formdata(data.items() if hasattr(data, 'items') else data)
        data = "Content-Type: {0}\r\n\r\n{1}".format(content_type, body)

        return super(Browser, self).post(url, data)

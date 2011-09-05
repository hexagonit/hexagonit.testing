from leo.testing.mech import LeoMechanizeBrowser
from leo.testing.mime import multipart_formdata
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
        but pass LeoMechanizeBrowser instance to mech_browser to use
        POST method for <form />s instead of GET method.

        :param app: Application object.
        :type app: object

        :param url: URL.
        :type url: str
        """
        super(z2.Browser, self).__init__(url=url, mech_browser=LeoMechanizeBrowser(app))

    def setBaseUrl(self, base_url):
        """Sets a base URL for all subsequent requests.
        Usually this url is portal_url.

        :param base_url: Base URL to avoide repetetive usage of the URL in testing.
        :type base_url: str
        """
        self._base_url = base_url

    def dump(self, filename):
        """Dumps the browser contents to the given file.

        :param filename: File name.
        :type filename: str
        """
        fh = open(filename, 'w')
        fh.write(self.contents)
        fh.close()

    def open(self, url, data=None):
        """Adds support for absolute paths without the base component.

        :param url: Absolute path.
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
        """Delete portlet manager of the name.

        Usually it is u'plone.leftcolumn' or u'plone.rightcolumn'.
        
        >>> column = getUtility(IPortletManager, name=name)
        >>> assignable = getMultiAdapter((portal, column), IPortletAssignmentMapping)
        >>> del assignable[name]
        
        :param portal: Portal object.
        :type portal: object

        :param name: Portlet manager name.
        :type name: unicode
        """

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
        with open(filepath, 'w') as file:
            file.write(self.contents)
        if browser == None:
            wbrowser = webbrowser
        else:
            wbrowser = webbrowser.get(browser)
        wbrowser.open_new_tab('file://' + filepath)

    def post(self, url, data):
        """Posting to url with multipart/form-data instead of application/x-www-form-urlencoded.

        :param url: where data will be posted.
        :type url: str

        :param data: Data which is a list of tuples for data posting.
        :type data: list
        """
        body, content_type = multipart_formdata(data)
        data = "Content-Type: {0}\r\n\r\n{1}".format(content_type, body)

        return super(Browser, self).post(url, data)

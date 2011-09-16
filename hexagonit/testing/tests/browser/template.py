from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter

import json


class EchoView(BrowserView):

    def __call__(self):
        return '\r\n'.join([
            'REQUEST_METHOD: {0}'.format(self.request['REQUEST_METHOD']),
            json.dumps(sorted(self.request.form.keys()))])


class TestFormView(BrowserView):

    index = ViewPageTemplateFile('templates/test_form.pt')

    def __call__(self):
        return self.index()

    def action_url(self):
        context_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_context_state')
        return '{object_url}/@@echo'.format(
            object_url=context_state.object_url(),
        )

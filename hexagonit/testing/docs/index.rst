.. include:: README.rst


Usage
-----

To use the enhanced test browser simple instantiate it in place of
``plone.testing.z2.Browser`` in your tests, e.g.

.. code-block:: python

    from hexagonit.testing.browser import Browser
    browser = Browser()

    # Set the base URL for easier browsing.
    browser.setBaseUrl(self.portal.absolute_url())

    # Access objects using readable URLs.
    browser.open('/my/cool-page')
    browser.open('/some/other/place')

    # Login in to the portal
    browser.login('r00t', 's3kr3t')

    # Inspect the current URL in a real browser.
    browser.openBrowser()

    # POST data directly without a <form>, including a file upload.
    browser.post('/web-api', {
        'foo': 'bar',
        'my_file_field': {
            'filename': 'my-document.pdf',
            'content-type': 'application/pdf',
            'data' : open('/tmp/my-document.pdf'),
            }
        })

API
---

.. automodule:: hexagonit.testing.browser

.. autoclass:: Browser
   :members:
   :member-order: bysource

Contents:

.. toctree::
    :maxdepth: 2

    INSTALL.rst
    HISTORY.rst
    CONTRIBUTORS.rst
    LICENSE.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. include:: README.rst


Browser testing
---------------

The `hexagonit.testing.browser` module provides an enhanced `zope.testbrowser
<http://pypi.python.org/pypi/zope.testbrowser>`_ test browser.

The main purpose is to make functional browser tests read easier by reducing the amount
of confusing setup code.

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


Date manipulation
-----------------

The `hexagonit.testing.date` module provides helpers to mock out the
dynamic constructors `datetime.date.today()` and `datetime.datetime.now()` by
providing class generators which produce instances of these classes that return
static values.

This is particularly useful when used in conjunction with the `mock
<http://www.voidspace.org.uk/python/mock/>`_ package during unit testing, e.g.

.. code-block:: python

    from hexagonit.testing.date import static_date
    from hexagonit.testing.date import static_datetime
    import datetime
    import mock
    import unittest

    class MyTestCase(unittest.TestCase):

        @mock.patch('my.module.datetime', static_datetime(datetime.datetime(2011, 12, 14, 12, 45)))
        @mock.patch('my.module.date', static_date(datetime.date(2011, 12, 14)))
        def test_something_that_uses_datetime(self):
            # Within the test your application code calling `datetime.now()` or `date.today()`
            # will always return the static values.
            pass

API
---

.. automodule:: hexagonit.testing.browser

.. autoclass:: Browser
   :members:
   :member-order: bysource

.. automodule:: hexagonit.testing.date

.. autofunction:: static_date

.. autofunction:: static_datetime

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


Installation
============

We assume that you are using zc.buildout and the plone.recipe.zope2instance
recipe to manage your project:

* Add ``leo.testing`` to the list of eggs to install, e.g.::

    [buildout]
    ...
    eggs =
        ...
        leo.testing

* Re-run buildout, e.g. with:

    $ ./bin/buildout

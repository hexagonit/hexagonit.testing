from setuptools import find_packages
from setuptools import setup

import os


long_description = (
    open(os.path.join("hexagonit", "testing", "docs", "README.rst")).read() + "\n" +
    open(os.path.join("hexagonit", "testing", "docs", "HISTORY.rst")).read() + "\n" +
    open(os.path.join("hexagonit", "testing", "docs", "CONTRIBUTORS.rst")).read()
)

setup(
    name='hexagonit.testing',
    version='1.1.1',
    description="Plone4 test helper which uses plone.testing and manuel.",
    # long_description=long_description,
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
    ],
    keywords='',
    author='Hexagon IT',
    author_email='oss@hexagonit.fi',
    url='',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['hexagonit'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'manuel',
        'mock',
        'plone.app.testing',
        'plone.testing',
        'setuptools',
        'unittest2',
    ],
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """,
)

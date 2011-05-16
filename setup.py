from setuptools import find_packages
from setuptools import setup
import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = read('leo', 'testing', 'version.txt').strip()

long_description = (
    read('leo', 'testing', 'docs', 'index.rst'))

setup(name='leo.testing',
      version=version,
      description="Plone4 test helper which uses plone.testing and manuel.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Hexagon IT',
      author_email='oss@hexagonit.fi',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['leo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
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

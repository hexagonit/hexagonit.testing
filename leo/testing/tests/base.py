from plone.app.testing import FunctionalTesting, IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
import unittest2 as unittest


class LeoTestingLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        import leo.testing.tests.browser
        self.loadZCML(package=leo.testing.tests.browser)


LEO_SAMPLE_FIXTURE = LeoTestingLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(LEO_SAMPLE_FIXTURE,), name="LeoTestingLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(LEO_SAMPLE_FIXTURE,), name="LeoTestingLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING

from plone.app.testing import FunctionalTesting, IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
import unittest2 as unittest


class LeoTestingLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
#        import leo.testing
#        self.loadZCML(package=leo.testing)
        import leo.testing.tests.browser
        self.loadZCML(package=leo.testing.tests.browser)
#        z2.installProduct(app, 'leo.testing')

#    def setUpPloneSite(self, portal):
#        """Set up Plone."""
        # Install into Plone site using portal_setup
#        self.applyProfile(portal, 'leo.testing:default')

#    def tearDownZope(self, app):
#        """Tear down Zope."""
#        z2.uninstallProduct(app, 'leo.testing')


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

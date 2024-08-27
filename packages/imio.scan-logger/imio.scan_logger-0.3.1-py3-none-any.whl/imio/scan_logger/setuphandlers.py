# -*- coding: utf-8 -*-
from plone import api
from plone.base.interfaces.installable import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "imio.scan_logger:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and quickinstaller."""
        return ["imio.scan_logger.upgrades"]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.
    site = api.portal.get()
    site.manage_permission("plone.restapi: Use REST API", ("Manager", "Site Administrator", "Contributor"), acquire=0)


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.

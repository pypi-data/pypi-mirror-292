# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from imio.scan_logger import _
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IImioScanLoggerLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ISettings(Interface):
    """Interface for the form fields."""

    notification_emails = schema.TextLine(title=_(u"Notification emails"), description=_("Can be separated by a comma"))

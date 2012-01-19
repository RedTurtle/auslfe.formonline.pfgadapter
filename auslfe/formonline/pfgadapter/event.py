# -*- coding: utf-8 -*-

from zope import interface
from zope.component.interfaces import IObjectEvent, ObjectEvent

class IFormOnlineFilledEvent(IObjectEvent):
    """Marker interface for an event raised when an IFormOnline content has been filled"""

    object = interface.Attribute("The subject of the event.")
    fields = interface.Attribute("Fields values submitted to the form.")

class FormOnlineFilledEvent(ObjectEvent):
    """Event fired when IFormOnlineContent has been succesfully filled"""
    interface.implements(IFormOnlineFilledEvent)

    def __init__(self, object, fields):
        ObjectEvent.__init__(self, object)
        self.fields = fields

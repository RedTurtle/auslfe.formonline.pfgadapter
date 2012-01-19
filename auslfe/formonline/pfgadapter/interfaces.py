# -*- coding: utf-8 -*-

from zope.interface import Interface
from Products.PloneFormGen.interfaces import IPloneFormGenActionAdapter

class IFormOnlineActionAdapter(IPloneFormGenActionAdapter):
    """Marker interface for the FormOnline adapter for PDF"""

class IFormSharingProvider(Interface):
    """Interface for a provider of sharing features"""
    
    def share(formonline, overseer):
        """Share permission on a generated formonline using to an overseer"""

class IFormOnlineComposer(Interface):
    """Interface for a component that can "fill" the generated FormOnline content"""
    
    def fill(fields, adapter):
        """
        Fill the formonline context with data inside fields.
        
        adapter is the PFG adapter from which the formonline has been generated.
        """

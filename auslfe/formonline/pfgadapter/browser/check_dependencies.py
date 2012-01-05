# -*- coding: utf-8 -*-

from zope.interface import implements, Interface, Attribute

from Products.Five import BrowserView

try:
    import auslfe.formonline.tokenaccess
    print auslfe.formonline.tokenaccess
    TOKENACCESS = True
except ImportError:
    TOKENACCESS = False 

class ICheckDependenciesView(Interface):
    """A view that check optional dependencies auslfe.formonline.tokenaccess"""
    
    tokenaccess = Attribute("True if auslfe.formonline.tokenaccess is installed")


class CheckDependenciesView(BrowserView):
    implements(ICheckDependenciesView)
    
    @property
    def tokenaccess(self):
        return TOKENACCESS
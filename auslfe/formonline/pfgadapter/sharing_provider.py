# -*- coding: utf-8 -*-

from zope.interface import implements
from auslfe.formonline.pfgadapter.interfaces import IFormSharingProvider

class SimpleSharingProvider(object):
    implements(IFormSharingProvider)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def share(self, formonline, overseer):
        """Gives to overseer the Editor role on formonline"""
        roles = list(formonline.get_local_roles_for_userid(userid=overseer))
        if 'Editor' not in roles:
            roles.append('Editor')
            formonline.manage_setLocalRoles(overseer,roles)
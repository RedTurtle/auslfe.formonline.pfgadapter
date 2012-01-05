# -*- coding: utf-8 -*-

import logging
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from auslfe.formonline.pfgadapter.config import PROJECTNAME, ADD_CONTENT_PERMISSION

from zope.i18nmessageid import MessageFactory
formonline_pfgadapterMessageFactory = MessageFactory('auslfe.formonline.pfgadapter')

logger = logging.getLogger("auslfe.formonline.pfgadapter")

def initialize(context):

    import content
    print content
    
    ##########
    # Add our content types
    # A little different from the average Archetype product
    # due to the need to individualize some add permissions.
    #
    # This approach borrowed from ATContentTypes
    #
    listOfTypes = listTypes(PROJECTNAME)

    content_types, constructors, ftis = process_types(
        listOfTypes,
        PROJECTNAME)
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        permission = ADD_CONTENT_PERMISSION
        utils.ContentInit(
            kind,
            content_types      = (atype,),
            permission         = permission,
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)

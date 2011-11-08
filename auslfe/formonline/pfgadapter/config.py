"""Common configuration constants
"""

## The Project Name
PROJECTNAME = 'auslfe.formonline.pfgadapter'

## Permission for content creation for most types
from Products.CMFCore.permissions import setDefaultRoles
ADD_CONTENT_PERMISSION = 'auslfe.formonline.pfgadapter: Add adapter'
setDefaultRoles(ADD_CONTENT_PERMISSION, ('Manager', ))

from AccessControl import ClassSecurityInfo
from Products.PloneFormGen.content.actionAdapter import FormActionAdapter, FormAdapterSchema
from Products.PloneFormGen import HAS_PLONE30
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.base import registerATCT
from auslfe.formonline.pfgadapter.config import PROJECTNAME
from Products.Archetypes.public import Schema, ReferenceField
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from auslfe.formonline.pfgadapter import formonline_pfgadapterMessageFactory as _
from Products.CMFCore.utils import getToolByName

try:
    from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
    from plone.i18n.normalizer.interfaces import IURLNormalizer
    URL_NORMALIZER = True
except ImportError:
    URL_NORMALIZER = False
from zope.component import queryUtility
from Products.Archetypes.config import RENAME_AFTER_CREATION_ATTEMPTS

class FormOnlineAdapter(FormActionAdapter):
    """A form action adapter that will create a FormOnline object (a page)
    and will save form input data in the text field of FormOnline"""

    schema = FormAdapterSchema.copy() + Schema((

        ReferenceField('formOnlinePath',
            required=True,
            relationship='relatesToFormOnline',
            widget = ReferenceBrowserWidget(
                allow_search = True,
                allow_browse = True,
                show_indexes = False,
                force_close_on_insert = True,
                label = _(u'label_formOnlinePath', default=u'FormOnline page path'),
                description = _(u'description_formOnlinePath', default=u'Select the path which will be saved FormOnline object containing form input data.'),
                )
            ),
    ))

    # Check for Plone versions
    if not HAS_PLONE30:
        finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

    meta_type      = 'FormOnlineAdapter'
    portal_type    = 'FormOnlineAdapter'
    archetype_name = 'Form Online Adapter'
    security       = ClassSecurityInfo()
    
    security.declarePrivate('onSuccess')
    def onSuccess(self, fields, REQUEST=None):
        """Called by form to invoke custom success processing."""
        
        # fields will be a sequence of objects with an IPloneFormGenField interface
        self.save_form(fields)
        
    def save_form(self, fields):
        """Creates a FormOnline object and saves form input data in the text field of FormOnline."""
        
        container_formonline = self.getFormOnlinePath()
        
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser():
            title = _(u'Form completed by an anonymous user')
        else:
            username = mtool.getAuthenticatedMember().getUserName()
            title = _(u'Form completed by %s' % username)
        
        formonline_id = self.idCreation(title,container_formonline)
        if formonline_id:
            container_formonline.invokeFactory(id=formonline_id,type_name='FormOnline')
            formonline = getattr(container_formonline,formonline_id)
            formonline.edit(title=title)

    def idCreation(self, title, container_formonline):
        """Creates a name for an object like its title."""
        new_id = self.generateNewId(title)
        if new_id is None:
            return False

        # make sure we have an id unique in the parent folder.
        unique_id = self.findUniqueId(new_id,container_formonline)
        if unique_id is not None:
            return unique_id

        return False
        
    def generateNewId(self,title):
        """Suggest an id from title."""
        # Can't work w/o a title
        if not title:
            return None

        # Don't do anything without the plone.i18n package
        if not URL_NORMALIZER:
            return None

        if not isinstance(title, unicode):
            charset = self.getCharset()
            title = unicode(title, charset)

        request = getattr(self, 'REQUEST', None)
        if request is not None:
            return IUserPreferredURLNormalizer(request).normalize(title)

        return queryUtility(IURLNormalizer).normalize(title)
    
    def findUniqueId(self, id, parent_folder):
        """Find a unique id in the parent folder, based on the given id, by
        appending -n, where n is a number between 1 and the constant
        RENAME_AFTER_CREATION_ATTEMPTS, set in config.py. If no id can be
        found, return None."""
        parent_ids = parent_folder.objectIds()
        check_id = lambda id, required: id in parent_ids
        invalid_id = check_id(id, required=1)
        if not invalid_id:
            return id

        idx = 1
        while idx <= RENAME_AFTER_CREATION_ATTEMPTS:
            new_id = "%s-%d" % (id, idx)
            if not check_id(new_id, required=1):
                return new_id
            idx += 1

        return None

registerATCT(FormOnlineAdapter, PROJECTNAME)
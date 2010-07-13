from AccessControl import ClassSecurityInfo
from Products.PloneFormGen.content.actionAdapter import FormActionAdapter, FormAdapterSchema
from Products.PloneFormGen import HAS_PLONE30
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.base import registerATCT
from auslfe.formonline.pfgadapter.config import PROJECTNAME
from Products.Archetypes.public import Schema, ReferenceField, TextField, StringField, RichWidget, StringWidget
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
from Products.ATContentTypes.configuration import zconf
from zope.pagetemplate.pagetemplatefile import PageTemplateFile

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
                description = _(u'description_formOnlinePath', default=u'Select the path which will be saved FormOnline pages containing form input data.'),
                )
            ),
                        
        TextField('adapterPrologue',
              required=False,
              validators = ('isTidyHtmlWithCleanup',),
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                    label = _(u'label_adapterPrologue', default=u'Adapter prologue'),
                    description = _(u'description_adapterPrologue', default=u'This text will be displayed above the form input data.'),
                    allow_file_upload = zconf.ATDocument.allow_document_upload
                    )
              ),
        
        StringField('formFieldOverseer',
              required=False,
              default="overseerEmail",
              widget = StringWidget(
                    label = _(u'label_formFieldOverseer', default=u'Name of form field that identifies the overseer'),
                    description = _(u'description_formFieldOverseer', default=u"Enter the name of form field used by the user completing the form to indicate the overseer's email."),
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
        formonline_url = self.save_form(fields)
        self.REQUEST.RESPONSE.redirect(formonline_url+'/edit')
        return
        
    def save_form(self, fields):
        """Creates a FormOnline object and saves form input data in the text field of FormOnline."""
        
        container_formonline = self.getFormOnlinePath()
        
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser():
            translate_title = getToolByName(self,'translation_service').translate(msgid='Form completed by an anonymous user',
                                                                                  domain="auslfe.formonline.pfgadapter",
                                                                                  default=u'Form completed by an anonymous user')
        else:
            username = mtool.getAuthenticatedMember().getUserName()
            translate_title = getToolByName(self,'translation_service').translate(msgid='Form completed by %s',
                                                                                  domain="auslfe.formonline.pfgadapter",
                                                                                  default=u'Form completed by %s') % username


        formonline_id = self.idCreation(translate_title,container_formonline)
        if formonline_id:
            container_formonline.invokeFactory(id=formonline_id,type_name='FormOnline')
            formonline = getattr(container_formonline,formonline_id)
            formonline.edit(title=translate_title)
            body_text = PageTemplateFile('formOnlineTextTemplate.pt').pt_render({'fields':fields,
                                                                                 'request':self.REQUEST,
                                                                                 'adapter_prologue':self.getAdapterPrologue()})
            formonline.edit(text=body_text)
            return formonline.absolute_url()
            
    def idCreation(self, title, container_formonline):
        """Creates a name for an object like its title."""
        new_id = self.generateNewIdFromTitle(title)
        if new_id is None:
            return False

        # make sure we have an id unique in the parent folder.
        unique_id = self.findUniqueId(new_id,container_formonline)
        if unique_id is not None:
            return unique_id

        return False
        
    def generateNewIdFromTitle(self,title):
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
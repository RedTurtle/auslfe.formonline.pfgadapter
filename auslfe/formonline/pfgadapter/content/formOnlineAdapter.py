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
from Products.PloneFormGen.config import FORM_ERROR_MARKER

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
                label = _(u'label_formOnlinePath', default=u'Form Online page path'),
                description = _(u'description_formOnlinePath', default=u'Select the path which will be saved Form Online pages containing form input data.'),
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
        """ Called by form to invoke custom success processing.
            return None (or don't use "return" at all) if processing is
            error-free.
            
            Return a dictionary like {'field_id':'Error Message'}
            and PFG will stop processing action adapters and
            return back to the form to display your error messages
            for the matching field(s).

            You may also use Products.PloneFormGen.config.FORM_ERROR_MARKER
            as a marker for a message to replace the top-of-the-form error
            message.

            For example, to set a message for the whole form, but not an
            individual field:

            {FORM_ERROR_MARKER:'Yuck! You will need to submit again.'}

            For both a field and form error:

            {FORM_ERROR_MARKER:'Yuck! You will need to submit again.',
             'field_id':'Error Message for field.'}
            
            Messages may be string types or zope.i18nmessageid objects.                
        """
        
        # fields will be a sequence of objects with an IPloneFormGenField interface
        
        check_result = self.checkOverseerEmail(fields)
        if type(check_result) == dict:
            # check_result contains a error
            return check_result
            
        formonline = self.save_form(fields)
        self.getEditorRoleToOverseer(formonline,check_result)
        self.REQUEST.RESPONSE.redirect(formonline.absolute_url()+'/edit')
        return
    
    def checkOverseerEmail(self,fields):
        """Checks if the email address of the assignee is provided in a form field.
           Returns the name of the user with that address or a error message."""
        
        found = False
        formFieldName = self.getFormFieldOverseer()
        ts = getToolByName(self,'translation_service')
        
        for field in fields:
            if field.__name__ == formFieldName.lower():
                overseerEmail = field.htmlValue(self.REQUEST)
                found = True
        if not found:
            error_message = ts.translate(msgid='error_nofield',domain='auslfe.formonline.pfgadapter',
                                         default=u'There is no field %s in the form to specify the overseer of the request.') % formFieldName
            return {FORM_ERROR_MARKER:error_message}
        
        if overseerEmail and (overseerEmail != 'No Input'):
            membership = getToolByName(self, 'portal_memberdata')
            users = membership.searchMemberDataContents('email',overseerEmail)
            if users:
#                if len(users) > 1:
#                    warning_message = ts.translate(msgid='error_multipleusers', domain='auslfe.formonline.pfgadapter',
#                                                   default=u'There are multiple users with the same email address provided for the field %s.') % formFieldName
#                    addStatusMessage(self.REQUEST, warning_message, type='warning')
                return users[0]['username']
            else:
                error_message = ts.translate(msgid='error_nouser', domain='auslfe.formonline.pfgadapter',
                                             default=u'No user corresponds to the email address provided, enter a new value.')
                return {formFieldName.lower():error_message}
        else:
            error_message = ts.translate(msgid='error_nospecifiedvalue', domain='auslfe.formonline.pfgadapter',
                                         default=u'The value of the field %s must be provided, enter the information requested.') % formFieldName
            return {formFieldName.lower():error_message}
        
    def getEditorRoleToOverseer(self,formonline,overseer):
        """Gives to overseer the Editor role on formonline"""
        roles = list(formonline.get_local_roles_for_userid(userid=overseer))
        if 'Editor' not in roles:
            roles.append('Editor')
            formonline.manage_setLocalRoles(overseer,roles)
        
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
        container_formonline.invokeFactory(id=formonline_id,type_name='FormOnline')
        formonline = getattr(container_formonline,formonline_id)
        formonline.edit(title=translate_title)
        body_text = PageTemplateFile('formOnlineTextTemplate.pt').pt_render({'fields':fields,
                                                                             'request':self.REQUEST,
                                                                             'adapter_prologue':self.getAdapterPrologue()})
        formonline.edit(text=body_text)
        return formonline
            
    def idCreation(self, title, container_formonline):
        """Creates a name for an object like its title."""
        new_id = self.generateNewIdFromTitle(title)

        # make sure we have an id unique in the parent folder.
        unique_id = self.findUniqueId(new_id,container_formonline)
        return unique_id
        
    def generateNewIdFromTitle(self,title):
        """Suggest an id from title."""

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

registerATCT(FormOnlineAdapter, PROJECTNAME)
# -*- coding: utf-8 -*-

from Acquisition import aq_parent
from zope import interface
from zope.annotation import IAnnotations
from AccessControl import ClassSecurityInfo, Unauthorized
from Products.CMFCore import permissions
from Products.PloneFormGen.content.actionAdapter import FormActionAdapter, FormAdapterSchema
try:
    from Products.PloneFormGen import HAS_PLONE30
except ImportError:
    HAS_PLONE30 = False
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.base import registerATCT
from auslfe.formonline.pfgadapter.config import PROJECTNAME
from Products.Archetypes.public import Schema, ReferenceField, TextField, StringField, RichWidget
from Products.Archetypes.public import StringWidget, SelectionWidget, BooleanWidget, BooleanField
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.CMFCore.utils import getToolByName
try:
    from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
    from plone.i18n.normalizer.interfaces import IURLNormalizer
    URL_NORMALIZER = True
except ImportError:
    URL_NORMALIZER = False
from zope.component import queryUtility, getMultiAdapter
from Products.ATContentTypes.configuration import zconf
from Products.PloneFormGen.config import FORM_ERROR_MARKER
from Products.PloneFormGen.content.fields import FGStringField

from auslfe.formonline.pfgadapter import logger
from auslfe.formonline.pfgadapter import formonline_pfgadapterMessageFactory as _
from auslfe.formonline.content.interfaces.formonline import IFormOnline
from auslfe.formonline.pfgadapter.interfaces import IFormOnlineActionAdapter, IFormSharingProvider
from auslfe.formonline.pfgadapter.interfaces import IFormOnlineComposer
from reStructuredText import HTML as rstHTML

class FormOnlineAdapter(FormActionAdapter):
    """A form action adapter that will create a FormOnline object (a page)
    and will save form input data in the text field of FormOnline"""

    interface.implements(IFormOnlineActionAdapter)

    schema = FormAdapterSchema.copy() + Schema((

        ReferenceField('formOnlinePath',
            required=True,
            relationship='relatesToFormOnline',
            widget = ReferenceBrowserWidget(
                allow_search = True,
                allow_browse = True,
                show_indexes = False,
                force_close_on_insert = True,
                label = _(u'label_formOnlinePath', default=u'Form Online storage'),
                description = _(u'description_formOnlinePath', default=u'Select the path where generated Form Online documents will be saved.'),
                )
            ),

        StringField('contentToGenerate',
              required=True,
              default_method='getDefaultContentType',
              enforceVocabulary=True,
              vocabulary_factory='plone.app.vocabularies.ReallyUserFriendlyTypes',
              widget = SelectionWidget(
                    label = _(u'label_contentToGenerate',
                              default=u'Document type to generate'),
                    description = _(u'description_contentToGenerate',
                                    default=u"Select a content type to be used.\n"
                                            u"When using the adapter and after saving the form, a new document of the selected type "
                                            u"will be created."),
                    )
              ),

        TextField('adapterPrologue',
              required=False,
              validators = ('isTidyHtmlWithCleanup',),
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                    label = _(u'label_adapterPrologue', default=u'Adapter prologue'),
                    description = _(u'description_adapterPrologue', default=u'This text will be included at the beginning of any Form Online generated.'),
                    allow_file_upload = zconf.ATDocument.allow_document_upload
                    )
              ),
        
        StringField('formFieldOverseer',
              required=False,
              default='None',
              vocabulary="vocabularyAllStringFields",
              widget = SelectionWidget(
                    label = _(u'label_formFieldOverseer',
                              default=u'Name of Form field that identifies the overseer.'),
                    description = _(u'description_formFieldOverseer',
                                    default=u"Enter the name of Form field used by the user completing the Form to indicate the overseer's email.\n"
                                            u"This field is required with the default worflow provided by this products, so leave empty only with the alternative ones.\n"
                                            u"Be careful."),
                    )
              ),

        BooleanField('overseerMustBeMember',
              required=False,
              schemata="anonymous access",
              widget = BooleanWidget(
                    condition = "object/@@checkDependencies/tokenaccess",
                    label = _(u'label_overseerMustBeMember',
                              default=u'Overseer must be a site member'),
                    description = _(u'description_overseerMustBeMember',
                                    default=u"Keep this checked to force the user e-mail address to be related to a site member.\n"
                                            u"Uncheck to use whatever address; in this case, if the address is not owned by any site member, a special e-mail with a secret token is sent."),
                    ),
              ),

        StringField('formFieldSubmitter',
              required=False,
              default='',
              schemata="anonymous access",
              vocabulary="vocabularyAllStringFields",
              widget = SelectionWidget(
                    label = _(u'label_formFieldSubmitter',
                              default=u'Name of the form field that keep the sender e-mail'),
                    description = _(u'description_formFieldSubmitter',
                                    default=u"Enter the name of a Form field where the user that submit the form must put it's own e-mail.\n"
                                             "Please not that this field is not required (and ignored) if the user is a site member.\n"
                                             "So: fill this field only if you plan to grant access to anonymous users."),
                    )
              ),
              
        StringField('formOnlineSubmitSubject',
              required=False,
              default_method='getDefaultSubmitSubject',
              schemata="notifications",
              widget = StringWidget(
                    label = _(u'label_formOnlineSubmitSubject',
                              default=u'Subject of email notification of submission of the form'),
                    description = _(u'description_formOnlineSubmitSubject',
                                    default=u"Enter the subject of the email notification will be sent when the Form Online generated will be submitted for approval."),
                    size=40,
                    )
              ),
              
        TextField('formOnlineSubmitMessage',
              required=False,
              default_method='getDefaultSubmitMessage',
              schemata="notifications",
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                    label = _(u'label_formOnlineSubmitMessage',
                              default=u'Text of email notification of submission of the form'),
                    description = _(u'description_formOnlineSubmitMessage',
                                    default=u"Enter the text of the email notification will be sent when the Form Online generated will be submitted for approval. \n"
                                             "Some content in this message may be replaced with ${} variables. \n"
                                             "The variable ${formonline_title} will be replaced with the title or id of Form Online generated. \n"
                                             "The variable ${insertion_date} will be replaced with the creation date of Form. \n"
                                             "The variable ${formonline_owner} will be replaced with the creator of Form. \n"
                                             "The variable ${formonline_url} will be replaced with the URL of Form. \n"
                                             "The variable ${comment} will be replaced with the comments may be added when the user change state of Form."),
                    )
              ),
              
        StringField('formOnlineApprovalSubject',
              required=False,
              default_method='getDefaultApprovalSubject',
              schemata="notifications",
              widget = StringWidget(
                    label = _(u'label_formOnlineApprovalSubject',
                              default=u'Subject of email notification of approval of the form'),
                    description = _(u'description_formOnlineApprovalSubject',
                                    default=u"Enter the subject of the email notification will be sent when the Form Online generated will be approved."),
                    size=40,
                    )
              ),
              
        TextField('formOnlineApprovalMessage',
              required=False,
              default_method='getDefaultApprovalMessage',
              schemata="notifications",
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                    label = _(u'label_formOnlineApprovalMessage',
                              default=u'Text of email notification of approval of the form'),
                    description = _(u'description_formOnlineApprovalMessage',
                                    default=u"Enter the text of the email notification will be sent when the Form Online generated will be approved. \n"
                                             "Some content in this message may be replaced with ${} variables. \n"
                                             "The variable ${formonline_title} will be replaced with the title or id of Form Online generated. \n"
                                             "The variable ${insertion_date} will be replaced with the creation date of Form. \n"
                                             "The variable ${formonline_owner} will be replaced with the creator of Form. \n"
                                             "The variable ${formonline_url} will be replaced with the URL of Form. \n"
                                             "The variable ${comment} will be replaced with the comments may be added when the user change state of Form."),
                    )
              ),
              
        StringField('formOnlineDispatchSubject',
              required=False,
              default_method='getDefaultDispatchSubject',
              schemata="notifications",
              widget = StringWidget(
                    label = _(u'label_formOnlineDispatchSubject',
                              default=u'Subject of email notification of dispatch of the form'),
                    description = _(u'description_formOnlineDispatchSubject',
                                    default=u"Enter the subject of the email notification will be sent when the Form Online generated will be dispatched."),
                    size=40,
                    )
              ),
              
        TextField('formOnlineDispatchMessage',
              required=False,
              default_method='getDefaultDispatchMessage',
              schemata="notifications",
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                    label = _(u'label_formOnlineDispatchMessage',
                              default=u'Text of email notification of dispatch of the form'),
                    description = _(u'description_formOnlineDispatchMessage',
                                    default=u"Enter the text of the email notification will be sent when the Form Online generated will be dispatched. \n"
                                             "Some content in this message may be replaced with ${} variables. \n"
                                             "The variable ${formonline_title} will be replaced with the title or id of Form Online generated. \n"
                                             "The variable ${insertion_date} will be replaced with the creation date of Form. \n"
                                             "The variable ${formonline_owner} will be replaced with the creator of Form. \n"
                                             "The variable ${formonline_url} will be replaced with the URL of Form. \n"
                                             "The variable ${comment} will be replaced with the comments may be added when the user change state of Form."),
                    )
              ),
              
        StringField('formOnlineRetractSubject',
              required=False,
              default_method='getDefaultRetractSubject',
              schemata="notifications",
              widget = StringWidget(
                    label = _(u'label_formOnlineRetractSubject',
                              default=u'Subject of email notification of retraction of the form'),
                    description = _(u'description_formOnlineRetractSubject',
                                    default=u"Enter the subject of the email notification will be sent when the Form Online generated will be retracted from approval or dispatch."),
                    size=40,
                    )
              ),
              
        TextField('formOnlineRetractMessage',
              required=False,
              default_method='getDefaultRetractMessage',
              schemata="notifications",
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                    label = _(u'label_formOnlineRetractMessage',
                              default=u'Text of email notification of rejection of the form'),
                    description = _(u'description_formOnlineRetractMessage',
                                    default=u"Enter the text of the email notification will be sent when the Form Online generated will be rejected from approval or dispatch. \n"
                                             "Some content in this message may be replaced with ${} variables. \n"
                                             "The variable ${formonline_title} will be replaced with the title or id of Form Online generated. \n"
                                             "The variable ${insertion_date} will be replaced with the creation date of Form. \n"
                                             "The variable ${formonline_owner} will be replaced with the creator of Form. \n"
                                             "The variable ${formonline_url} will be replaced with the URL of Form. \n"
                                             "The variable ${comment} will be replaced with the comments may be added when the user change state of Form."),
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
        
        mtool = getToolByName(self, 'portal_membership')
        utool = getToolByName(self, 'plone_utils')
        wtool = getToolByName(self, 'portal_workflow')
        
        # fields will be a sequence of objects with an IPloneFormGenField interface
        check_fieldOverseer = self.checkFieldOverseer(fields)
        if type(check_fieldOverseer) == dict:
            return check_fieldOverseer
           
        try:
            formonline = self.save_form(fields)
        except ValueError:
            utool.addPortalMessage(_(u'You are not authorized to write on this folder.'), type='error')
            return
        except Unauthorized:
            utool.addPortalMessage(_(u'You are not authorized to fill that form.'), type='error')
            return

        # Share the form with the proper user only if a Overseer is provided and the proper workflow has to be used.
        if check_fieldOverseer[1]:
            sharing_provider = getMultiAdapter((self, self.REQUEST), IFormSharingProvider,
                                           name='provider-for-%s' % check_fieldOverseer[0])
            sharing_provider.share(formonline, check_fieldOverseer[1])
            
        if mtool.isAnonymousUser():
            check_fieldSubmitter = self.checkFieldSubmitter(fields)
            if type(check_fieldSubmitter) == dict:
                return  check_fieldSubmitter

            formFieldSubmitterName = self.getFormFieldSubmitter()
            if formFieldSubmitterName:
                # Memoize the e-mail, for later notification
                for field in fields:
                    if field.fgField.getName() == queryUtility(IURLNormalizer).normalize(formFieldSubmitterName):
                        IAnnotations(formonline)['owner-email'] = field.htmlValue(self.REQUEST)
                        break
            
            # Immediatly submit the form (he can't edit it later)
            wtool.doActionFor(formonline, 'submit')
            utool.addPortalMessage(_(u'Your data has been sent.'), type='info')
            #self.REQUEST.RESPONSE.redirect(self.aq_parent.absolute_url())
            return
        else:
            # Playing with the workflow you can allow owners to modify the document
            # right after its creation. Below the check for the proper redirect URL
            if formonline.restrictedTraverse('@@plone_context_state').is_editable():
                utool.addPortalMessage(_(u'Feel free to modify your data'), type='info')
                self.REQUEST.RESPONSE.redirect(formonline.absolute_url()+'/edit')
            else:
                self.REQUEST.RESPONSE.redirect(formonline.absolute_url()+'/view')
                
    security.declarePrivate('getDefaultContentType')
    def getDefaultContentType(self):
        default = self.getField('contentToGenerate').Vocabulary(self).getValue('FormOnline')
        return default and 'FormOnline' or 'Document'
    
    security.declarePrivate('getDefaultSubmitSubject')
    def getDefaultSubmitSubject(self):
        _ = getToolByName(self,'translation_service').translate
        return _(msgid='subject_pending_approval',
                 default=u'[Form Online] - Form Online in pending state approval',
                 domain="auslfe.formonline.pfgadapter",
                 context=self)
    
    security.declarePrivate('getDefaultSubmitMessage')
    def getDefaultSubmitMessage(self):
        _ = getToolByName(self,'translation_service').translate    
        rstText = _(msgid='mail_text_approval_required', default=u"""Dear user,

this is a personal communication regarding the Form Online **${formonline_title}**, created on **${insertion_date}** by **${formonline_owner}**.

It is waiting for your approval. Follow the link below for perform your actions:

${formonline_url}

Regards
""", domain="auslfe.formonline.pfgadapter", context=self)
        return rstHTML(rstText,input_encoding='utf-8',output_encoding='utf-8')

    security.declarePrivate('getDefaultApprovalSubject')
    def getDefaultApprovalSubject(self):
        _ = getToolByName(self,'translation_service').translate
        return _(msgid='subject_pending_dispatch',
                 default=u'[Form Online] - Form Online in pending state dispatch',
                 domain="auslfe.formonline.pfgadapter",
                 context=self)

    security.declarePrivate('getDefaultApprovalMessage')
    def getDefaultApprovalMessage(self):
        _ = getToolByName(self,'translation_service').translate
        rstText = _(msgid='mail_text_dispatch_required', default=u"""Dear user,

this is a personal communication regarding the Form Online **${formonline_title}**, created on **${insertion_date}** by **${formonline_owner}**.

The request has been approved and it's waiting for your confirmation. Follow the link below for perform your actions:

${formonline_url}

Regards
""", domain="auslfe.formonline.pfgadapter", context=self)
        return rstHTML(rstText,input_encoding='utf-8',output_encoding='utf-8')

    security.declarePrivate('getDefaultDispatchSubject')
    def getDefaultDispatchSubject(self):
        _ = getToolByName(self,'translation_service').translate
        return _(msgid='subject_dispatched',
                 default=u'[Form Online] - Form Online approved',
                 domain="auslfe.formonline.pfgadapter",
                 context=self)

    security.declarePrivate('getDefaultDispatchMessage')
    def getDefaultDispatchMessage(self):
        _ = getToolByName(self,'translation_service').translate
        rstText = _(msgid='mail_text_dispatched', default=u"""Dear user,

this is a personal communication regarding the Form Online **${formonline_title}**.

The request has been *approved*. Follow the link below to see the document:

${formonline_url}

Regards
""", domain="auslfe.formonline.pfgadapter", context=self)
        return rstHTML(rstText,input_encoding='utf-8',output_encoding='utf-8')
    
    security.declarePrivate('getDefaultRetractSubject')
    def getDefaultRetractSubject(self):
        _ = getToolByName(self,'translation_service').translate
        return _(msgid='subject_rejected',
                 default=u'[Form Online] - Form Online rejected',
                 domain="auslfe.formonline.pfgadapter",
                 context=self)
    
    security.declarePrivate('getDefaultRetractMessage')
    def getDefaultRetractMessage(self):
        _ = getToolByName(self,'translation_service').translate
        rstText = _(msgid='mail_text_rejected', default=u"""Dear user,

this is a personal communication regarding the Form Online **${formonline_title}**.

The request has been *rejected*. The overseer provided the following comment::

${comment}

Follow the link below to see the document:

${formonline_url}

Regards
""", domain="auslfe.formonline.pfgadapter", context=self)
        return rstHTML(rstText,input_encoding='utf-8',output_encoding='utf-8')

    security.declarePrivate('vocabularyAllStringFields')
    def vocabularyAllStringFields(self):
        form = aq_parent(self)
        fields = form.objectValues()
        return [('None',_('None'))] + [(content.id, content.title) for content in fields if isinstance(content, FGStringField)]
    
    def checkFieldSubmitter(self, fields):
         # We take care of the "formFieldSubmitter" info only for anonymous
        formFieldSubmitterName = self.getFormFieldSubmitter()
        _ = getToolByName(self, 'translation_service').translate

        ownerEmail = None
        if formFieldSubmitterName:
            for field in fields:
                if field.__name__ == queryUtility(IURLNormalizer).normalize(formFieldSubmitterName):
                    ownerEmail = field.htmlValue(self.REQUEST)
                    break
            if not ownerEmail:
                error_message = _('error_nofieldownermail',
                                  default=u'There is no field "${email_field}" in the Form to specify the owner of the request.',
                                  context=self,
                                  domain='auslfe.formonline.pfgadapter',
                                  mapping={'email_field':  formFieldSubmitterName}
                                  )
                return {FORM_ERROR_MARKER: error_message}

    security.declarePrivate('checkFieldOverseer')
    def checkFieldOverseer(self, fields):
        """
        Checks if the email address of the assignee is provided in a form field.
        
        Possible returns values:
        * a tuple with ('email', eMailAddress)
        * a dict with error message
        """

        formFieldName = self.getFormFieldOverseer()
        _ = getToolByName(self, 'translation_service').translate

        overseerEmail = None
        hasOverseerField = False
        overseerMustBeMember = self.getOverseerMustBeMember()
        tokenaccessInstalled = self.restrictedTraverse('@@checkDependencies').tokenaccess

        #verify if the form cotains overseer filed and get the value
        for field in fields:
            if field.__name__ == queryUtility(IURLNormalizer).normalize(formFieldName):
                hasOverseerField = True
                overseerEmail = field.htmlValue(self.REQUEST)
                break
        
        #if Overseer set as empty return error 
        if hasOverseerField and not overseerEmail:
            error_message = _('error_overseer_email',
                              default=u'No Overseer email has been provided, enter a new value.',
                              context=self,
                              domain='auslfe.formonline.pfgadapter',
                              )
            return {queryUtility(IURLNormalizer).normalize(formFieldName): error_message}
        

        if hasOverseerField and overseerEmail != 'No Input':
            membership = getToolByName(self, 'portal_memberdata')
            users = membership.searchMemberDataContents('email', overseerEmail)
            if users:
                if len(users) > 1:
                    logger.warning('There are multiple users with the same email address provided for the field %s.' % formFieldName)
#                    warning_message = ts.translate(msgid='error_multipleusers', domain='auslfe.formonline.pfgadapter',
#                                                   default=u'There are multiple users with the same email address provided for the field %s.') % formFieldName
#                    addStatusMessage(self.REQUEST, warning_message, type='warning')
                return ('user', users[0]['username'])
            elif overseerMustBeMember or not tokenaccessInstalled:
                error_message = _('error_nouser',
                                  default=u'No user corresponds to the email address provided, enter a new value.',
                                  context=self,
                                  domain='auslfe.formonline.pfgadapter',
                                  )
                return {queryUtility(IURLNormalizer).normalize(formFieldName): error_message}
            else:
                # Here only if no user found but also we are not forced to have a site member
                # Also auslfe.formonline.tokenaccess is installed
                return ('email', overseerEmail)
        else:
            return ('email', '')

    def save_form(self, fields):
        """Creates a FormOnline object and saves form input data in the text field of FormOnline."""
        
        container_formonline = self.getFormOnlinePath()
        ctype = self.getContentToGenerate()

        formonline_id = container_formonline.generateUniqueId(ctype)
        container_formonline.invokeFactory(id=formonline_id, type_name=ctype)
        formonline = getattr(container_formonline, formonline_id)
        # disable the automatically change of id based on title
        formonline.unmarkCreationFlag()
        
        # If the content doesn't implements the proper interface: mark it!
        if not IFormOnline.providedBy(formonline):
            interface.alsoProvides(formonline, IFormOnline)
            formonline.reindexObject(idxs=['object_provides'])
                
        # Now fill the content
        IFormOnlineComposer(formonline).fill(fields, self)
        # Attach the information of which Form Online Adapter  
        IAnnotations(formonline)['formOnlineAdapter'] = self.UID()
        return formonline


registerATCT(FormOnlineAdapter, PROJECTNAME)

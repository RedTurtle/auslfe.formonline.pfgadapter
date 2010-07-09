from AccessControl import ClassSecurityInfo
from Products.PloneFormGen.content.actionAdapter import FormActionAdapter, FormAdapterSchema
from Products.PloneFormGen import HAS_PLONE30
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.base import registerATCT
from auslfe.formonline.pfgadapter.config import PROJECTNAME
from Products.Archetypes.public import Schema, ReferenceField
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from auslfe.formonline.pfgadapter import formonline_pfgadapterMessageFactory as _

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
        self.save_form(fields, REQUEST)
        
    def save_form(self, fields, request, **kwargs):
        """Save the form.
        """
        print "Hello World"
#        self.context.invokeFactory(id=newId,type_name='LPE')
#        newlpe=getattr(self.context,newId)
#        newlpe.edit(title=nome,matricola=mtr,nomeequipe=nome,codicereparto=codr,prestazione=prst,
#                codiceprestazione=codp,branca=br,costoineuro=cost)
#        newlpe.reindexObject()


registerATCT(FormOnlineAdapter, PROJECTNAME)
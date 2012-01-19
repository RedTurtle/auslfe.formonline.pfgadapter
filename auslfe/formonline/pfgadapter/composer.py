# -*- coding: utf-8 -*-

from Acquisition import aq_parent
from zope.interface import implements
from zope.pagetemplate.pagetemplatefile import PageTemplateFile

from Products.CMFCore.utils import getToolByName
from auslfe.formonline.pfgadapter.interfaces import IFormOnlineComposer

class BasicFormOnlineComposer(object):
    """
    Basic implementation: fill title and body text.
    Filling text field of the target document using an HTML from the provided template.
    """
    implements(IFormOnlineComposer)
    
    def __init__(self, context):
        self.context = context
    
    def fill(self, fields, adapter):
        """See IFormOnlineComposer documentation"""
        context = self.context
        form_title = aq_parent(adapter).Title()
        mtool = getToolByName(context, 'portal_membership')
        _ = getToolByName(context, 'translation_service').translate

        if mtool.isAnonymousUser():
            translate_title = _('Form completed by an anonymous user',
                                default=u'Form "$form_name" completed by an anonymous user',
                                context=context,
                                domain='auslfe.formonline.pfgadapter',
                                mapping={'form_name': form_title}
                                )
        else:
            username = mtool.getAuthenticatedMember().getUserName()
            translate_title = _('Form completed by',
                                default=u'Form "$form_name" completed by $user',
                                context=context,
                                domain='auslfe.formonline.pfgadapter',
                                mapping={'user': username, 'form_name': form_title}
                                )

        body_text = PageTemplateFile('./browser/formOnlineTextTemplate.pt').pt_render(
                                            {'fields': fields,
                                             'request': context.REQUEST,
                                             'adapter_prologue': adapter.getAdapterPrologue()}
        )

        # do not use .edit as this is not working when using auslfe.formonline.tokenaccess
        #formonline.edit(text=body_text, title=translate_title)
        context.setTitle(translate_title)
        context.setText(body_text)
        context.reindexObject()

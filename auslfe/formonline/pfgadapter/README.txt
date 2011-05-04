.. contents:: **Table of contents**

Before beginning our tour, let's configure some of the underlying stuff.

    >>> from Products.Five.testbrowser import Browser
    >>> from Products.PloneTestCase.setup import default_password
    >>> browser = Browser()
    >>> portal_url = self.portal.absolute_url()
    >>> self.portal.error_log._ignored_exceptions = ()

Now let's configure the site areas.

    >>> self.generateITArea()
    'Created: Information Technology Department'

Configuration of the Form Online
================================

The main idea
-------------

A company department want to use Form Online to manage users requests. The first need is an online form
for handle users request to obtain internet connection from their PCs.

The IT department has its own area in the site.

    >>> browser.open(portal_url)
    >>> browser.getLink('Information Technology Department').click()

Inside this area, we also have a specific section for users that wanna ask to enable a Internet connection.

    >>> browser.getLink('Internet activation').click()

Configuration of the PFG
------------------------

There, we can host our PloneFormGen. First let's login as ``Manager``.

    >>> browser.getLink('Log in').click()
    >>> browser.getControl(name='__ac_name').value = 'uber_user'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

Then we create our PFG.

    >>> browser.getLink('Add new').click()
    >>> browser.getControl('Form Folder').click()
    >>> browser.getControl(name='form.button.Add').click()

Now, let's fill some values

    >>> browser.getControl(name='title').value = 'Request for Internet activation'
    >>> browser.getControl(name='description').value = ('Fill this form to ask for obtaining Web access from your work PC.\n'
    ...                                                 'An authorization from your responsible will be required.')
    >>> browser.getControl('Mailer').click()
    
We don't need any "Thanks page". We can disable it.
    
    >>> browser.getControl('None').click()
    
Now we save and publish the PFG.
    
    >>> browser.getControl('Save').click()
    >>> 'Changes saved.' in browser.contents
    True
    >>> browser.getLink('Publish').click()
    >>> 'Item state changed.' in browser.contents
    True

Before customize the PFG with our additional fields, we can remove useles stuff.

    >>> browser.getLink('Contents').click()
    >>> browser.getLink('All').click()
    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted.' in browser.contents
    True

The form for this example will contains only two fields, plus a required field for make Form Online working.

    >>> browser.getLink('Add new').click()
    >>> browser.getControl('String Field').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> browser.getControl(name='title').value = 'IP'
    >>> browser.getControl(name='description').value = 'Put there the IP address of you machine'
    >>> browser.getControl('Required').click()
    >>> browser.getControl('Save').click()
    Traceback (most recent call last):
    ...
    HTTPError: HTTP Error 404: Not Found
    >>> browser.open(portal_url+'/information-technology-department/internet-activation/request-for-internet-activation')
    >>> browser.getLink('Add new').click()
    >>> browser.getControl('Checkbox Field').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> browser.getControl(name='title').value = 'Need to access Web sites outside the Company proxy'
    >>> browser.getControl(name='description').value = ('Check this if you need special access to Web sites that are not commonly '
    ...                                                 'permitted by our Uber Company Proxy')
    >>> browser.getControl('Save').click()
    Traceback (most recent call last):
    ...
    HTTPError: HTTP Error 404: Not Found
    >>> browser.open(portal_url+'/information-technology-department/internet-activation/request-for-internet-activation')

The last field is *really important*, and it must be an e-mail address (not the e-mail address of the user, so this is
why we deleted the default e-mail field).

    >>> browser.getLink('Add new').click()
    >>> browser.getControl('String Field').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> browser.getControl(name='title').value = "Your superior's e-mail"
    >>> browser.getControl(name='description').value = ('Put there the e-mail address of the person in charge of validate your request, '
    ...                                                 'before the IT department will be able to enable your IP.')
    >>> browser.getControl('Required').click()
    >>> browser.getControl('Is an E-Mail Address').click()
    >>> browser.getControl('Save').click()
    Traceback (most recent call last):
    ...
    HTTPError: HTTP Error 404: Not Found
    >>> browser.open(portal_url+'/information-technology-department/internet-activation/request-for-internet-activation')

Now we can configure our adapter (and really use this product!).

Configuration of the adapter
----------------------------

When installing our Form Online product, the only new thing we can use for now is an additional PDF Adapter.

    >>> browser.getLink('Add new').click()
    >>> browser.getControl('Form Online Adapter').click()
    >>> browser.getControl(name='form.button.Add').click()

Now let's fill the data needed.

    >>> browser.getControl('title').value = 'Form Online generator'

We need to specify mainly a folder where to store all generated forms. By default (but you can put it everywhere in
the site) we can use the section itself. Use the reference browsing UI, like for related contents selection.

    >>> store_uid = portal.unrestrictedTraverse('/information-technology-department/internet-activation').UID()
    >>> browser.getControl(name='formOnlinePath').value = store_uid

Then we can put a form prologue. this prologue will be added in the head of every generated form.

    >>> browser.getControl('Adapter prologue').value = """<h1>Form for requesting Internet activation</h2>
    ... <p>
    ... Please, give me access to the World Wide Web!
    ... </p>
    ... <p>
    ... Here follow data for my request.
    ... </p>
    ... """

The last, important, field is the e-mail addreww name of the PDF field. The default is the same we used above when
we added an e-mail field to the PFG. You can still there put any title you gave to the field.

    >>> browser.getControl('Name of Form field that identifies the overseer').value = 'Form Online generator'

As you see, this field is required. You *must* have added that field to the PFG. 

    >>> browser.getControl('Save').click()
    Traceback (most recent call last):
    ...
    HTTPError: HTTP Error 404: Not Found
    >>> browser.open(portal_url+'/information-technology-department/internet-activation/request-for-internet-activation')

Last sugar
----------

The PFG section is ready. We can start use it but, for a better user experience, we also
make the PDF a default page for the "*Internet activation*" section

    >>> browser.getLink('Internet activation').click()
    >>> browser.getLink('Display').click()
    >>> browser.getLink('Choose a content item').click()
    >>> browser.getControl('Request for Internet activation').click()
    >>> browser.getControl('Save').click()
    >>> 'View changed.' in browser.contents
    True
    >>> browser.url.endswith('/information-technology-department/internet-activation/')
    True

So, from now, when users visit the "*Internet activation*" section, they will se our PFG.

How to use
==========

The logic
---------

XXX

.. contents:: **Table of contents**

First of all
============

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

We will explain this application with an example.

The main idea
-------------

A company department want to use Form Online to manage users requests. The first need is an online form
for handle users request to obtain Internet connection from their PCs.

The IT department has its own area in the site.

    >>> browser.open(portal_url)
    >>> browser.getLink('Information Technology Department').click()

Inside this area, we also have a specific section for users that wanna ask to enable a Internet connection.

    >>> browser.getLink('Internet activation').click()

Here is schema of the site structure we will create there::

    siteroot
        |
        |- ...
        |
        |- Information Technology Department (Folder)
        |                   |
        |                   |- ...
        |                   |
        |                   |- Internet activation (Folder)
        |                  ...          |
        |                               |- Request for Internet activation (PFG)
        |                               |- Form Online
        |                               |- Form Online
        |                               |- ...
        |                               \- Form Online
        |
        |
        |
       ...


Configuration of the PFG
------------------------

There, we can host our PloneFormGen. First let's login as ``Manager``.

    >>> browser.getLink('Log in').click()
    >>> browser.getControl(name='__ac_name').value = 'uber_user'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.getLink('Internet activation').click()

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
    >>> browser.getControl(name='title').value = "Your boss e-mail"
    >>> browser.getControl(name='description').value = ('Put there the e-mail address of the person in charge of validate your request, '
    ...                                                 'before the IT department will be able to enable your IP.')
    >>> browser.getControl('Required').click()
    >>> browser.getControl('Is an E-Mail Address').click()
    >>> browser.getControl('Save').click()
    Traceback (most recent call last):
    ...
    HTTPError: HTTP Error 404: Not Found
    >>> browser.open(portal_url+'/information-technology-department/internet-activation/request-for-internet-activation')

Note that we used an e-mail validator (given from PloneFormGen) and that we changed the default field value.
Now we can configure our adapter (and really use this product!).

Configuration of the adapter
----------------------------

When installing our Form Online product, the only new thing we can use for now is an additional PFG Adapter.

    >>> browser.getLink('Add new').click()
    >>> browser.getControl('Form Online Adapter').click()
    >>> browser.getControl(name='form.button.Add').click()

Now let's fill the data needed.

    >>> browser.getControl(name='title').value = 'Form Online generator'

We need to specify mainly a folder where to store all generated forms. By default (but you can put it everywhere in
the site) we can use the section itself. Use the reference browsing UI, like for related contents selection.

    >>> store_uid = portal.unrestrictedTraverse('information-technology-department/internet-activation').UID()
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

Now we can also select the content type we want to use as Form Online. The default value can "Form Online" itself
if the proper Generic Setup import step has been executed, fallback simply to a Plone "Page".

Of course, other values are possible; for example we can use a News Item!

    >>> browser.getControl('Document type to generate').value = ['News Item']

But *keep in mind* that you need to use the workflow given with the product for this content type (setting
this globally or using CMFPlacefulWorkflow).

    >>> self.portal.portal_workflow.setChainForPortalTypes(['News Item'], ('formonline_workflow'),)

The last, important, field is the e-mail address name of the PFG field. The default is the same we used above when
we added an e-mail field to the PFG. You can still there put any title you gave to the field.

    >>> browser.getControl('Name of Form field that identifies the overseer').value = 'Your boss e-mail'

As you see, this field is required. You *must* have added that field to the PFG. 

    >>> browser.getControl(name='form.button.save').click()
    Traceback (most recent call last):
    ...
    HTTPError: HTTP Error 404: Not Found
    >>> browser.open(portal_url+'/information-technology-department/internet-activation/request-for-internet-activation')

Last sugar
----------

The PFG section is ready. We can start use it but, for a better user experience, we also
make the form folder to be default page for the "*Internet activation*" section

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

For a general overview of the workflow, see the main documentation.

Permissions on the site
-----------------------

There are mainly *3 actors*:

* the user, that works inside the "Department A" of the Company, that require the authorization for the
  Internet access: ``user_dep_a``
* The overseer of the "Department A", that is responsible of ``user_dep_a`` actions: ``boss_dep_a``
* The IT Manager, or whoever inside the "Department IT" take care of enable Internet access: ``it_manager``

One of the guys that need a special role on a section of the site is ``it_manager``. We must give to him the *Reviewer*
role on the folder that will keep all the generated form for Internet activation.

    >>> browser.open(portal_url+'/information-technology-department/internet-activation')
    >>> browser.getLink('Sharing').click()
    >>> browser.getLink('go here').click()
    >>> browser.url.endswith('/information-technology-department/internet-activation/sharing')
    True
    >>> browser.getControl(name='search_term').value = 'IT Manager'
    >>> browser.getControl(name='form.button.Search').click()
    >>> browser.getControl(name='entries.role_Reviewer:records').controls[1].selected = True
    >>> browser.getControl('Save').click()
    >>> 'Changes saved.' in browser.contents
    True

Now simple users. All users we want be able to fill the Form Online need to be *Contributor* on the folder choosen
for host filled forms.

    >>> browser.open(portal_url+'/information-technology-department/internet-activation')
    >>> browser.getLink('Sharing').click()
    >>> browser.getLink('go here').click()
    >>> browser.url.endswith('/information-technology-department/internet-activation/sharing')
    True
    >>> browser.getControl(name='search_term').value = 'User A'
    >>> browser.getControl(name='form.button.Search').click()
    >>> browser.getControl(name='entries.role_Contributor:records').controls[0].selected = True
    >>> browser.getControl('Save').click()
    >>> 'Changes saved.' in browser.contents
    True

No more configuration is needed from now (the Boss need an account on the site, but can be one that never user the
site).

    >>> browser.getLink('Log out').click()

User that fill the form
-----------------------

Let's now begin to act as *User A*, the one that needs to ask for Internet activation.

    >>> browser.open(portal_url+'/login_form')
    >>> browser.getControl(name='__ac_name').value = 'user_dep_a'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> 'User A' in browser.contents
    True

What special permission it need in the site? *No one*! It simply need to be able to reach the prepared PFG, so
the Company workflow make the difference there (if you want to prepare reserved PFG, for private Form Online, just
put it in a private folder).

Now, move on to our PFG.

    >>> browser.getLink('Information Technology Department').click()
    >>> browser.getLink('Internet activation').click()

User A can now fill the form.

    >>> browser.getControl('IP').value = '10.0.1.75'
    >>> browser.getControl('Need to access Web sites outside the Company proxy').click()

A *very important* (and I hope you put it required) field is the "*Overseer email*" data.
User A needs to put there an e-mail address of a user in charge of validate the request. See the main documentation
for knowing more.

    >>> browser.getControl('Your boss e-mail').value = 'boss_dep_a@mycompany.gov'

He can now save and submit the request.

    >>> browser.getControl('Submit').click()

Where he's now? The user can now manually modify the Form Online content, that is more or less like a simple page.

    >>> browser.url.endswith('/edit')
    True

For example, he can change the auto-filled title. This is however optional; the user at this point can simply save and
confirm data.

    >>> browser.getControl('Title').value = 'Activation for Internet access for IP 10.0.1.75'
    >>> browser.getControl('Save').click()

Again, the user can modify this form later. This until he submit it.

    >>> 'The form has not been submitted yet.' in browser.contents
    True
    >>> browser.getLink('Submit for approval').click()
    >>> 'Overseer has not approved this form yet.' in browser.contents
    True

The user from now can't edit anymore the document.

    >>> browser.getLink('Edit')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

The user has ended his cicle now. He must wait for approval.

    >>> browser.getLink('Log out').click()

Other users?
------------

The User A can still see his form, as you saw above. What about other users?

    >>> browser.open(portal_url+'/login_form')
    >>> browser.getControl(name='__ac_name').value = 'user_dep_b'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> 'User B' in browser.contents
    True

User B is of another department. We don't know what are the power of that user, but we don't care.
Is only important to know that he:

* can generate another request for Internet activation
* can't see generated request from User A

    >>> browser.getLink('Information Technology Department').click()
    >>> browser.getLink('Internet activation').click()
    >>> 'Activation for Internet access for IP 10.0.1.75' in browser.contents
    False

That's all

    >>> browser.getLink('Log out').click()

Overseer
--------

Let's became the Boss of User A.

    >>> browser.open(portal_url+'/login_form')
    >>> browser.getControl(name='__ac_name').value = 'boss_dep_a'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> 'Boss A' in browser.contents
    True

The Boss has no special power on the site, but as User A named him (using it's e-mail) as overseer, he now
behave a *Editor* role onto the generated document.

    >>> browser.getLink('Information Technology Department').click()
    >>> browser.getLink('Internet activation').click()
    >>> 'Activation for Internet access for IP 10.0.1.75' in browser.contents
    True
    >>> browser.getLink('Activation for Internet access for IP 10.0.1.75').click()

As form editor, we can accept it, refuse our authorization and also edit the form for changing something.
Keep in mind that changes done by the Boss are still saved through the versioning feature given by Plone.

    >>> browser.getLink('Edit')
    <Link text='Edit' ...>
    >>> browser.getLink('Approve content')
    <Link text='Approve content' ...>
    >>> browser.getLink('Retract content')
    <Link text='Retract content' ...>

Let's approve the request.

    >>> browser.getLink('Approve content').click()
    >>> 'This activity has not been confirmed yet.' in browser.contents
    True

Now we can't do anything else there (but we can still see the content).

    >>> browser.getLink('Edit')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

We can forget the Boss now

    >>> browser.getLink('Log out').click()

The final step
--------------

The final actor is the IT Manager.

    >>> browser.open(portal_url+'/login_form')
    >>> browser.getControl(name='__ac_name').value = 'it_manager'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> 'IT Manager' in browser.contents
    True

This user has (must have) a *Reviewer* role on the whole section. This because this user can (must) accept/reject
*all* filled Form Online for this kind of request, for dispatching them.

Different from the *Editor* role, given to one user on the single document, the filled form section can also have
a group of many *Reviewer*.

Obviously other sections of the site can have other PFG with Form Online adapter, that will generate different
requests that IT Manager doesn't care about.

    >>> browser.getLink('Information Technology Department').click()
    >>> browser.getLink('Internet activation').click()
    >>> 'Activation for Internet access for IP 10.0.1.75' in browser.contents
    True
    >>> browser.getLink('Activation for Internet access for IP 10.0.1.75').click()

The Reviewer can't edit the data, but can perform the final dispatch action.

    >>> browser.getLink('Edit')
    Traceback (most recent call last):
    ...
    LinkNotFoundError
    >>> browser.getLink('Dispatch content').click()
   >>> 'Item state changed.' in browser.contents
   True

Now User A will be able to surf the Internet!


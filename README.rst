.. contents:: **Table of contents**
   :depth: 2

Introduction
============

The *Form Online* product is a Plone add-on composed by three modules:

* `PloneFormGen`__ (needed dependency)
* `auslfe.formonline.content`__ (needed dependency)
* A PloneFormGen *adapter* (auslfe.formonline.pfgadapter itself)

__ http://plone.org/products/ploneformgen
__ http://pypi.python.org/pypi/auslfe.formonline.content

It is designed for intranets or web sites. Using this, users of the site can handle on-line some company specific
tasks. Some example:

* ask for technical assistance from the IT Department
* plan user vacations with the Administration/Human Resource office
* ask to the administration to buy something expensive

This is designed keeping in mind not-too-large sized companies.

How to use it
=============

The general structure
---------------------

This product is heavily based on the PFG features. You can create the form, where you ask for user information, as you
want.

.. image:: http://keul.it/images/plone/auslfe.formonline.pfgadapter-0.2.0-01.png
   :alt: A custom form done using PloneFormGen

The only required field (but you can name/configure it as you want) is an e-mail field end the user will fill with
his overseer address (see below).

After that you must use the new *PFG adapter*: Form Online Adapter

Before being ready to use the form, you need to choose a place (a Folder, or a Large Folder if you think to manage a lot
of requests).

If you will use multiple PFG with Form Online Adapter (more than an online form), you can also use multiple
storages.

It's important to know that:

* *every* user that must be able to use a specific Form Online, need to have the *Contributor* role on the storage
  folder (play with the "Restriction" link inside the "Add new" to limit the user power to create other contents).
* the user(s) who finally perform the request dispatch must be *Reviewer* on that folder.

.. image:: http://keul.it/images/plone/auslfe.formonline.pfgadapter-0.3.0-01.png
   :alt: An example of configuration of the PFG adapter

Default Workflow (formonline_workflow)
--------------------------------------

Let's explaing the default workflow (3-steps).

Actors
~~~~~~

There are three main actor in the life-cycle of a form:

* the user that "ask for something" (A)
* his *overseer*, that must approve the request (B)
* the technical user, that dispatch the request and take care that some action will be taken (C)

When user A ask for something, he always need to receive user B authorization before any other action can be taken.

To simplify the process and not being forced to have a Company Organization Chart, is user A itself that "choose"
who is his overseer. This is done by A writing down the B's e-mail address when filling the form.

When saving, user B will receive special power onto the generated form, so he can go there and edit, reject or
approve the form.

When he finally choose to accept the request, the game goes to user C, that is the one who perform some action.

Users receive e-mail address when the request need their attention.

Wait! Is user A that choose user B?!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As said above: this is targeted on small companies. If user A put the e-mail address of someone that isn't is boss,
or simply is own e-mail (so auto-approving), user C is aways the last step of the procedure. He's responsible to check if
user B is really one of the company overseer.

Simple Workflow (formonline_single_steps_workflow)
--------------------------------------------------

When overseer's approval is not necessary "Simple workflow" allows end users to submit a form and ask for dispatch
directly.

In order to achive this goal, "Form Online" type has to be configured to use this alternative workflow. You can do
this changing the workflow globally for the types, or enabling *CMFPlacefulWorkflow* product, available in
every Plone site.

Simple Workflow actors
~~~~~~~~~~~~~~~~~~~~~~

* the user that "ask for something"(A)
* the technical user, that dispatch the request and take care that some action will be taken (C)

When user A ask for something, the request goes directly to C that is the one who perform some action.

Users receive e-mail address when the request need their attention.

No user B is needed there.

Generated content type
----------------------

The basic installation of `auslfe.formonline.content`__ try to be simple as possible.
It provide a required workflow for working with the PFG Adapter, and the "Form Online"
content types.

__ http://pypi.python.org/pypi/auslfe.formonline.content

You can also choose to use another content type  when configuring the adapter, from the
"*Document type to generate*" field.
The adapter can work with whatever content type you want (it need to behave a text field, like Page and News
Items). But in this way you must configure other stuff, like assigning the proper worlflow to the content type
(globally, or locally using `CMFPlacefulWorkflow`__).

__ http://pypi.python.org/pypi/Products.CMFPlacefulWorkflow

Alternative configuration
=========================

Anonymous submitter
-------------------

You can also configure your Plone site to allow anonymous users to fill the form and generate contents.
What you simply need is to give to ``Anonymous`` role following permission:

* ``auslfe.formonline.content: Add FormOnline``
* ``Request review``

For *security reason* is better to give those permissions only onto the folder where you want to store generated
document.

You can do this using a specific workflow for that folder (maybe using a workflow policy)
or (**not suggested**) simply giving this permission directly from ZMI on the target folder.

In that case you can also use the "*Name of the form field that keep the sender e-mail*" adapter field,
so the anonymous user can leave his e-mail, to be notified later.

Anonymous overseer
------------------

If you want the overseer e-mail address to be (potentially) an *external* address, you can take a look at
`auslfe.formonline.tokenaccess`__.

__ http://pypi.python.org/pypi/auslfe.formonline.tokenaccess

Dependencies
============

This product has been tested with:

* Plone 3.3 (PloneFormGen 1.6.5)
* Plone 4.2 (PloneFormGen 1.7.1)

TODO
====

* We are planning an integration of the PFG adapter with `Easy Template`__
* Automatically save the overseer e-mail in the user data, so automatically fill future requests

__ http://pypi.python.org/pypi/collective.easytemplate/

Credits
=======

Developed with the support of:

* `Azienda USL Ferrara`__
  
  .. image:: http://www.ausl.fe.it/logo_ausl.gif
     :alt: Azienda USL's logo
  
* `S. Anna Hospital, Ferrara`__

  .. image:: http://www.ospfe.it/ospfe-logo.jpg 
     :alt: S. Anna Hospital - logo

All of them supports the `PloneGov initiative`__.

__ http://www.ausl.fe.it/
__ http://www.ospfe.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/


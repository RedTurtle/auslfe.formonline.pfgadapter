Introduction
============

The *Form Online* product is a Plone add-on composed by three modules:

* `PloneFormGen`__ (needed dependency) 
* auslfe.formonline.pfgadapter itself
* `auslfe.formonline.content`__

__ http://plone.org/products/ploneformgen
__ http://pypi.python.org/pypi/auslfe.formonline.content

It is designed for intranets or web sites. Using this, users of the site can handle on-line some company specific
tasks. Some example:

* ask for technical assistance from the IT Department
* plan user vacations with the Administration
* ask to the administration to buy something expensive
* ...

This is thinked for not-too-large sized companies.

How to use
==========

The general structure
---------------------

This product is heavily based on the PFG features. You can create the form, where you ask for user information, as you
want.

.. image:: http://keul.it/images/plone/auslfe.formonline.pfgadapter-0.2.0-01.png
   :alt: A custom form done using PloneFormGen

The only required field (but you can name/configure it as you want) if an e-mail field the the user will fill with
his overseer address (see below).

After that you must use the new *PFG adapter*: Form Online Adapter 

Before beeing ready to use the form, you need to choose a place (a Folder, or a Large Folder if you think to manage a lot
of requests).

If you will use multiple PFG with Form Online Adapter, you can also use multiple storages.

It's important to know that:

* *every* user that must be able to use a specific Form Online, need to have the *Contributor* role on the storage
  folder (play with the "Restriction" link inside the "Add new" to limit the user power to create other contents).
* the user(s) who finally perform the request dispatch must be *Reviewer* on that folder.

.. image:: http://keul.it/images/plone/auslfe.formonline.pfgadapter-0.2.0-02.png
   :alt: A custom form done using PloneFormGen

The actors
----------

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
------------------------------------

As said above: this is targeted on small companies. If user A put the e-mail address of someone that isn't is boss,
or simply is own e-mail (so auto-approving), user C is aways the last step of the procedure. He's responsible to check if
user B is really one of the company overseer.

Dependencies
============

This product has been developed with:

* Plone 3.3
* PloneFormGen 1.6.0

TODO
====

* Plone 4 compatibility
* We are planning an integration of the PFG adapter with `Easy Template`__
* Automatically save the overseer e-mail in the user data, so automatically fill future requests
* A shorter workflow, for very simple approvation where we only need A and C actors

__ http://pypi.python.org/pypi/collective.easytemplate/

Credits
=======

Developed with the support of `Azienda USL Ferrara`__; Azienda USL Ferrara supports the
`PloneGov initiative`__.

.. image:: http://www.ausl.fe.it/logo_ausl.gif
   :alt: Azienda USL's logo

__ http://www.ausl.fe.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.net/

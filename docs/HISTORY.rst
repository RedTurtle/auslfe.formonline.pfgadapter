Changelog
=========

0.7.3 (unreleased)
------------------

- Nothing changed yet.


0.7.2 (2014-10-28)
------------------

- Fixed translations [keul]

0.7.1 (2012-10-03)
------------------

* Fixed italian translations [keul]
* Raised the subject's field default size [keul]
* Fixed dependencies [keul]
* Fixed a bug: "edit" power were tested on
  the adapter object, not form online [keul]

0.7.0 (2012-09-17)
------------------

* a new workflow has been added (simple workflow) [nicola.senno]
* redirect check. If the owner doesn't have "Modify portal content" permission
  it won't be able to modify the document after submission.

0.6.0 (2012-07-12)
------------------

Updated to Plone 4.2

* fix translation of mail_text_rejected, missed literal block [fdelia]
* added fields to FormOnlineAdapter for subject and text of notification email [fdelia]
* moved fields related to work with anonymous to a separate fieldset [keul]
* now the required e-mail field names are taken from a dropdown of all PFG string field
  (do not need to write it manually anymore) [keul]
* enable by default the "withtypes" profile of ``auslfe.formonline.content`` [keul]

0.5.0 (2012-01-20)
------------------

* removed old unused code [keul]
* moved the form-filling procedure to a ``IFormOnlineComposer`` adapter: 3rd party code
  could customize how the ``IFormOnline`` is filled [keul]
* added a new "*Name of the form field that keep the sender e-mail*" field in the
  adapter (for use the product with anonymous submitters) [keul]

0.4.1 (2012-01-15)
------------------

* FormOnlineAdapter now removed from searchable/navigation types [keul]
* a general approach to the e-mail adapter, simpler for developers to customize it using
  a browserlayer interface [keul]

0.4.0 (2012-01-11)
------------------

* fixed translations [keul]
* added a soft dependency on ``auslfe.formonline.tokenacces`` [keul]

0.3.0 (2011-12-13)
------------------

First pubic release

* documentation fixes
* light support for "Site Administrator" role (this **not** mean that we tested this on Plone 4.1 yet)
  [keul]
* added a new "contentToGenerate" field, for choosing the content type to be generated [keul]

0.2.0 (2011-05-06)
------------------

* better i18ndude support [keul]
* mail sending refactoring [keul]
* added an ``Unauthorized`` check in the current user can't write in the storage
  folder [keul]
* translations changes [keul]
* added documentation and manual [keul]
* egg cleanup and dependencies checks [keul]

0.1.0 (2010-07-19)
------------------

* Initial release [fdelia]

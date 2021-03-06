#!/bin/sh

DOMAIN='auslfe.formonline.pfgadapter'

i18ndude rebuild-pot --pot locales/${DOMAIN}.pot --create ${DOMAIN} .
i18ndude merge --pot locales/${DOMAIN}.pot --merge locales/${DOMAIN}-manual.pot
i18ndude sync --pot locales/${DOMAIN}.pot locales/*/LC_MESSAGES/${DOMAIN}.po

DOMAIN='plone'

i18ndude merge --pot i18n/${DOMAIN}-formonline.pot --merge i18n/${DOMAIN}-manual.pot
i18ndude sync --pot i18n/${DOMAIN}-formonline.pot i18n/${DOMAIN}-formonline-??.po

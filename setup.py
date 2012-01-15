from setuptools import setup, find_packages
import os

version = '0.4.1'

setup(name='auslfe.formonline.pfgadapter',
      version=version,
      description="An adapter for PloneFormGen that add to Plone a way for manage online forms submission",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 3.3",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plonegov form plone',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/auslfe.formonline.pfgadapter',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['auslfe', 'auslfe.formonline'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.PloneFormGen',
          'auslfe.formonline.content',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

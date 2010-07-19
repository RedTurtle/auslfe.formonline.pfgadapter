from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(name='auslfe.formonline.pfgadapter',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['auslfe', 'auslfe.formonline'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.PloneFormGen',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

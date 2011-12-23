# -*- coding: utf-8 -*-
"""
This module contains the tool of pytheon.deploy
"""
import os
import sys
from setuptools import setup, find_packages

PY3 = sys.version_info[0] == 3

def read(*rnames):
    filename = os.path.join(os.path.dirname(__file__), *rnames)
    if os.path.isfile(filename):
        return open(filename).read()
    return ''

version = '0.1'

long_description = (
    read('README.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('pytheon', 'deploy', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
   'Download\n'
    '********\n')

if PY3:
    tests_require = ['zope.testing', 'zc.buildout']
    install_requires = ['setuptools',
                        'zc.buildout',
                        'collective.recipe.template',
                        'z3c.recipe.scripts',
                        'gp.vcsdevelop>=2.2',
                        'ConfigObject',
                        'PasteDeploy',
                        'SQLAlchemy',
                        #'gunicorn',
                        #'supervisor',
                        'pytheon',
                        'Genshi',
                       ]
else:
    tests_require = ['zope.testing', 'zc.buildout', 'unittest2', 'Django']
    install_requires = ['setuptools',
                        'zc.buildout',
                        'collective.recipe.template',
                        'z3c.recipe.scripts',
                        'gp.vcsdevelop>=2.2',
                        'ConfigObject',
                        'PasteDeploy',
                        'PasteScript',
                        'SQLAlchemy',
                        'gunicorn',
                        'supervisor',
                        'pytheon',
                        'Genshi',
                       ]

kw = dict(version='.'.join([str(i) for i in sys.version_info[:2]]))
if PY3:
    from distutils.command.build_py import build_py_2to3 \
        as build_py
    kw['cmdclass'] = {'build_py': build_py},

setup(name='pytheon.deploy',
      version=version,
      description="",
      long_description=long_description,
      # Get more strings from
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='buildout recipe pytheon',
      author='Bearstech',
      author_email='py@bearstech.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pytheon'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='pytheon.deploy.tests.test_docs.test_suite',
      entry_points="""
      [zc.buildout]
      default = pytheon.deploy.recipes:Deploy
      scripts = pytheon.deploy.recipes:Scripts
      wsgi = pytheon.deploy.recipes:Wsgi
      apache = pytheon.deploy.recipes:Apache
      nginx = pytheon.deploy.recipes:Nginx

      [console_scripts]
      pytheon-admin = pytheon.deploy.scripts:admin
      pytheon-admin-%(version)s = pytheon.deploy.scripts:admin
      build-eggs = pytheon.deploy.scripts:build_eggs
      """ % kw,
      )

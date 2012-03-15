# -*- coding: utf-8 -*-
"""
Doctest runner for 'pytheon.deploy'.
"""
__docformat__ = 'restructuredtext'

import unittest
import zc.buildout.tests
import zc.buildout.testing

from zope.testing import doctest, renormalizing
import zope.testing.DocFileCase


optionflags =  (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE |
                doctest.REPORT_ONLY_FIRST_FAILURE)


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)

    # Install the recipe in develop mode
    zc.buildout.testing.install_develop('meld3', test)
    zc.buildout.testing.install_develop('Genshi', test)
    zc.buildout.testing.install_develop('Django', test)
    zc.buildout.testing.install_develop('pytheon', test)
    zc.buildout.testing.install_develop('gunicorn', test)
    zc.buildout.testing.install_develop('supervisor', test)
    zc.buildout.testing.install_develop('ConfigObject', test)
    zc.buildout.testing.install_develop('SQLAlchemy', test)
    zc.buildout.testing.install_develop('Paste', test)
    zc.buildout.testing.install_develop('PasteDeploy', test)
    zc.buildout.testing.install_develop('PasteScript', test)
    zc.buildout.testing.install_develop('zc.recipe.egg', test)
    zc.buildout.testing.install_develop('gp.vcsdevelop', test)
    zc.buildout.testing.install_develop('z3c.recipe.scripts', test)
    zc.buildout.testing.install_develop('collective.recipe.template', test)
    zc.buildout.testing.install_develop('pytheon.deploy', test)

    # Install any other recipes that should be available in the tests
    #zc.buildout.testing.install('collective.recipe.foobar', test)

globs = {}


class TestCase(DocFileCase):

    def __new__(*args, **kwargs):
        return doctest.DocFileTest(
                '../README.txt',
                setUp=setUp,
                tearDown=zc.buildout.testing.buildoutTearDown,
                optionflags=optionflags,
                checker=renormalizing.RENormalizing([
                        # If want to clean up the doctest output you
                        # can register additional regexp normalizers
                        # here. The format is a two-tuple with the RE
                        # as the first item and the replacement as the
                        # second item, e.g.
                        # (re.compile('my-[rR]eg[eE]ps'), 'my-regexps')
                        zc.buildout.testing.normalize_path,
                        ]),
                )

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

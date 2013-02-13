# -*- coding: utf-8 -*-
"""
Doctest runner for 'pytheon.deploy'.
"""
__docformat__ = 'restructuredtext'

import os
import unittest
import zc.buildout.tests
import zc.buildout.testing

from zope.testing import renormalizing
import doctest


optionflags = (doctest.ELLIPSIS |
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
    zc.buildout.testing.install_develop('zc.recipe.egg==1.3.2', test)
    zc.buildout.testing.install_develop('gp.vcsdevelop', test)
    zc.buildout.testing.install_develop('z3c.recipe.scripts', test)
    zc.buildout.testing.install_develop('collective.recipe.template', test)
    zc.buildout.testing.install_develop('pytheon.deploy', test)

    # Install any other recipes that should be available in the tests
    #zc.buildout.testing.install('collective.recipe.foobar', test)

    zc.buildout.easy_install.default_index_url = 'http://pypi.python.org/simple'
    os.environ['buildout-testing-index-url'] = (
        zc.buildout.easy_install.default_index_url
    )

globs = {}


class TestCase(doctest.DocFileCase):

    def __init__(self, *args, **kwargs):
        parser = doctest.DocTestParser()
        self.path = os.path.join(os.path.dirname(__file__), '..', 'README.txt')
        self.name = os.path.basename(self.path)
        doc = open(self.path).read()
        test = parser.get_doctest(doc, globals(), self.name, self.path, 0)

        # init doc test case
        doctest.DocFileCase.__init__(self, test, optionflags=optionflags,
                setUp=setUp,
                tearDown=zc.buildout.testing.buildoutTearDown,
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

    def shortDescription(self):
        return self.path

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

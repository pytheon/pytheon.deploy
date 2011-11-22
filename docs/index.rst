.. pytheon.deploy documentation master file, created by
   sphinx-quickstart on Mon Nov 21 14:37:12 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pytheon.deploy's documentation!
==========================================

Contents:

.. toctree::
   :maxdepth: 2

About
=====

pytheon.deploy allow you to build an hosting environment for shared server.

The idea is to use a single command to deploy a python application.

Installation
============

Get the bootstrap_ script. And run it::

  $ mkdir /opt/pytheon
  $ cd /opt/pytheon
  $ python pytheon_bootstrap.py

Get more eggs!
==============

By default the bootstrap script install a minimalistic set of eggs.
You can use the ``-extend`` options to extend the installation at run time::

  $ python pytheon_bootstrap.py -extend [django|http://url.to.your/config.cfg]

If the option is a simple term the it will look at the pytheon repository to
find the ``.cfg``.  See the `available files`_

You can always change this stuff in ``{prefix}/etc/pytheon/pytheon.ini`` later.

You can now build all that stuff::

  $ bin/build-eggs

By default this will download eggs for the python versions of the interpreter
used to bootstrap pytheon but you can use a different one or more than one::

  $ bin/build-eggs -i 2.6 -i 3.2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _bootstrap: https://raw.github.com/pytheon/pytheon.deploy/master/deploy/pytheon_bootstrap.py
.. _available files: https://github.com/pytheon/pytheon.deploy/tree/master/deploy

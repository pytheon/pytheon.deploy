========================
Installation and upgrade
========================

Installation
============

Get the bootstrap_ script. And run it::

  $ PREFIX=/opt/pytheon
  $ mkdir $PREFIX
  $ cd $PREFIX
  $ python pytheon_bootstrap.py


Upgrading
=========

Just run then ``pytheon-upgrade`` script::

    $ $PREFIX/bin/pytheon-upgrade

Get more eggs!
==============

By default the bootstrap script install a minimalistic set of eggs.
You can use the ``--extend`` options to extend the installation at run time::

  $ python pytheon_bootstrap.py --extend [django|http://url.to.your/config.cfg]

If the option is a simple term the it will look at the pytheon repository to
find the ``.cfg``.  See the `available files`_

You can always change this stuff in ``{prefix}/etc/pytheon/pytheon.ini`` later.

You can now build all that stuff::

  $ bin/build-eggs

By default this will download eggs for the python versions of the interpreter
used to bootstrap pytheon but you can use a different one or more than one::

  $ bin/build-eggs -i 2.6 -i 3.2

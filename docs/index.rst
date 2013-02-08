Welcome to pytheon.deploy's documentation!
==========================================

About
=====

**pytheon.deploy** features :

* allow you to build an hosting environment for shared server
* deploy your application on this hosting environment

The idea is to use a single command to deploy all your python applications.


Quick start
===========

On your Debian server, download Pytheon `sample_buildout <https://github.com/pytheon/sample_buildout>`_ :

.. code-block:: sh

    $ mkdir ~/projects/
    $ cd ~/projects/
    $ git clone git@github.com:pytheon/sample_buildout.git
    $ cd sample-buildout

Next, use ``pytheon-bootstrap.py`` to install **pytheon.deploy** component :

.. code-block:: sh

    $ python pytheon-bootstrap.py

Now you can deploy your application :

.. code-block:: sh

    $ bin/pytheon-admin -d . --host=my-app.example.com

| Application is installed in ``~/root/sample_buildout`` folder.

* you can start your application daemon with ``~/root/sample_buildout/bin/pytheond``
* use ``~/root/sample_buildout/etc/apache.conf`` in your Apache configuration

If you want test full stack in VM, you can read « :doc:`vagrant` » page.

Contents
========

.. toctree::
   :maxdepth: 2

   install.rst
   configuration.rst
   deploy.rst
   vagrant.rst
   tips.rst
   contribute.rst

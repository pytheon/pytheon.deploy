===========================================
Test Pytheon full stack easily with Vagrant
===========================================

``vagrant/`` folder contains script to install automatically *Pytheon* in
`Vagrant <http://www.vagrantup.com/>`_ virtual machine (Development environments made
easy).


Prerequisites
=============

On Ubuntu 12.10
---------------

Prerequisites :

.. code-block:: sh

    $ sudo apt-get install virtualbox rubygem1.8


Pytheon vagrant installation environment
========================================

Fetch `pytheon.deploy <https://github.com/pytheon/pytheon.deploy>`_

.. code-block:: sh

    $ mkdir -p ~/projects
    $ cd ~/projects
    $ git clone https://github.com/pytheon/pytheon.deploy.git
    $ cd pytheon.deploy/vagrant/

Install Python dependencies (fabric…) with *buildout* :

.. code-block:: sh

    $ python bootstrap.py
    $ bin/buildout


Install pytheon in vagrant VM
=============================

Download and start *vagrant* VM :

.. code-block:: sh

    $ vagrant up

Execute *fabric* install :

.. code-block:: sh

    $ bin/fab vagrant install_pytheon


Uninstall Pytheon in vagrant VM
===============================

You can uninstall Pytheon with this command :

.. code-block:: sh

    $ bin/fab vagrant uninstall_pytheon

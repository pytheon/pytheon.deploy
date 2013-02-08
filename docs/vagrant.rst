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

Install this vagrant plugin, `vagrant-hostmaster <https://github.com/mosaicxm/vagrant-hostmaster>`_  to
manage ``/etc/hosts`` entries on both the host OS and guest VMs.

.. code-block:: sh

    $ vagrant gem install vagrant-hostmaster
    

Install pytheon in vagrant VM
=============================

Download and start *vagrant* VM :

.. code-block:: sh

    $ vagrant up

Execute *fabric* command (here ``master`` branch is selected but you can also select ``dev`` branch) :

.. code-block:: sh

    $ bin/fab vagrant master install_pytheon


.. Note:: 

    By default, ``install_pytheon`` use ``pytheon_bootstrap.py`` located in current working copy ``../deploy`` folder.

    If you want to use remote version ``https://raw.github.com/pytheon/pytheon.deploy/master/deploy/pytheon_bootstrap.py`` you can use this command :

    .. code-block:: sh

        $ bin/fab vagrant remote_bootstrap install_pytheon

      
Deploy *sample_buildout*
========================

Before deploy *sample_buildout* you need to install pytheon (``bin/fab vagrant install_pytheon``)

Execute *fabric* command :

.. code-block:: sh

    $ bin/fab vagrant install_sample_buildout

.. Note:: 

    By default, ``install_sample_buildout`` use ``sample_buildout`` located ``vagrant/src/sample_buildout`` folder.

    If you want to use remote version ``git@github.com:pytheon/sample_buildout.git`` you can use this command :

    .. code-block:: sh

        $ bin/fab vagrant remote_sample_buildout install_sample_buildout


``install_sample_buildout`` task install *sample_buildout* application in ``/home/user1/root/``.

You can test that ``sample_builout`` is well started.

.. code-block:: sh

    $ curl http://example.com
    Hello world!
    
It's work !


Uninstall Pytheon in vagrant VM
===============================

You can uninstall Pytheon with this command :

.. code-block:: sh

    $ bin/fab vagrant uninstall_pytheon


Uninstall *sample_buildout*
===========================

You can uninstall *sample_buildout* with this command :

.. code-block:: sh

    $ bin/fab vagrant uninstall_sample_buildout

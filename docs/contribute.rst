=============================
Contribute to Pytheon project
=============================

Clone, install and launch the tests
===================================

Clone the project in your working folder :

.. code-block:: sh

    $ git clone git@github.com:pytheon/pytheon.deploy.git

Initialise the project with *buildout* :

.. code-block:: sh

    $ cd pytheon.deploy
    $ python bootstrap.py
    $ bin/buildout

.. Warning::

    Do not use buildout in a virtualenv here otherwise you'll get some issue (see : https://github.com/buildout/buildout/issues/56 )

Launch the tests :

.. code-block:: sh

    $ bin/nosetests 
    .
    Name             Stmts   Miss  Cover   Missing
    ----------------------------------------------
    pytheon.deploy      28      8    71%   18-21, 24-26, 29, 42
    ----------------------------------------------------------------------
    Ran 1 test in 23.273s

    OK


Install Pytheon **dev** branch environment
==========================================

Download ``pytheon_bootstrap.py`` in **dev** branch and use ``--branch`` parameter to install
**dev** *pytheon* dev branch version.

.. code-block:: sh

  $ curl -O https://raw.github.com/pytheon/pytheon.deploy/dev/deploy/pytheon_bootstrap.py
  $ PREFIX=/opt/pytheon
  $ mkdir $PREFIX
  $ cd $PREFIX
  $ python pytheon_bootstrap.py --branch=dev

This command install the *dev* branch of `pytheon <https://github.com/pytheon/pytheon/tree/dev>`_ and 
`pytheon.deploy <https://github.com/pytheon/pytheon.deploy/tree/dev>`_ repositories.


Develop in vagrant
==================

| If you are on Mac OSX system, it's difficult to contribute to *pythen.deploy*.
| But you can working in Vagrant environment.

First, read and execute « :ref:`pytheon-vagrant-installation` » section.

After Vagrant VM started.

Install some devlopment tools :

.. code-block:: sh

    $ bin/fab vagrant install_develop_tools

Connect you via ssh :

.. code-block:: plain

    $ vagrant ssh
    vagrant@pytheon:~$ tree -L 3
    .
    └── projects
        └── pytheon.deploy
            ├── bootstrap.py
            ├── buildout.cfg
            ├── CHANGES.txt
            ├── clean.sh
            ├── CONTRIBUTORS.txt
            ├── deploy
            ├── docs
            ├── etc
            ├── MANIFEST.in
            ├── pytheon
            ├── README.txt
            ├── requirements.txt
            ├── setup.cfg
            ├── setup.py
            └── vagrant

You have access to *pytheon.deploy* project in Vagrant VM, you can always edit *pytheon.deploy* source
code from your Host, with your favorite text editor.

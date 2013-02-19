==============================================
Pytheon environment installation and upgrading
==============================================

Pytheon environment installation
================================

Get the bootstrap_ script. And run it :

.. code-block:: sh

  $ PREFIX=/opt/pytheon
  $ mkdir $PREFIX
  $ cd $PREFIX
  $ curl -O https://raw.github.com/pytheon/pytheon.deploy/master/deploy/pytheon_bootstrap.py
  $ python pytheon_bootstrap.py

.. _bootstrap: https://raw.github.com/pytheon/pytheon.deploy/master/deploy/pytheon_bootstrap.py


Pytheon environment upgrading
=============================

Just run then ``pytheon-upgrade`` script :

.. code-block:: sh

    $ $PREFIX/bin/pytheon-upgrade


Files installed
===============

After installation, you have this structure in ``$PREFIX`` folder :

::

    ├── bin
    │   ├── backup-db
    │   ├── build-eggs
    │   ├── buildout
    │   ├── create-mysql-db
    │   ├── pytheon-admin
    │   ├── pytheon-admin-2.6
    │   └── pytheon-upgrade
    ├── eggs
    │   ├── collective.recipe.template-1.9-py2.6.egg
    │   ├── ConfigObject-1.2.2-py2.6.egg
    │   ├── distribute-0.6.34-py2.6.egg
    │   ├── distribute-0.6.34.tar.gz
    │   ├── Genshi-0.6-py2.6.egg
    │   ├── gp.vcsdevelop-2.2.3-py2.6.egg
    │   ├── gunicorn-0.17.2-py2.6.egg
    │   ├── meld3-0.6.10-py2.6.egg
    │   ├── Paste-1.7.5.1-py2.6.egg
    │   ├── PasteDeploy-1.5.0-py2.6.egg
    │   ├── PasteScript-1.7.5-py2.6.egg
    │   ├── pytheon-0.1-py2.6.egg
    │   ├── pytheon.deploy-0.1-py2.6.egg
    │   ├── SQLAlchemy-0.7.9-py2.6.egg
    │   ├── supervisor-3.0b1-py2.6.egg
    │   ├── z3c.recipe.scripts-1.0.1-py2.6.egg
    │   ├── zc.buildout-1.7.0-py2.6.egg
    │   └── zc.recipe.egg-1.3.2-py2.6.egg
    ├── etc
    │   └── pytheon
    │       └── pytheon.ini
    ├── lib
    │   └── pytheon
    │       └── buildout
    │           ├── buildout.cfg
    │           ├── develop-eggs
    │           └── parts
    │               ├── bootstrap
    │               │   ├── sitecustomize.py
    │               │   └── site.py
    │               └── pytheon
    │                   ├── sitecustomize.py
    │                   └── site.py
    └── pytheon_bootstrap.py



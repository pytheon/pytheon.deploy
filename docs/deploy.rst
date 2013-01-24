===========
Deployement
===========

Basic deployement
=================

The deployement is done with the ``pytheon-admin`` script:

.. sourcecode:: bash

    $ PYTHEON_ADMIN=$PREFIX/bin/pytheon-admin

You need a git or hg repository:

.. sourcecode:: bash

    $ $PYTHEON_ADMIN -d git://example.com/myapp.git --host=mydomain.com

This will install a tree in ``~/root``

By default you will have:

- Apache and nginx configs in ``~/root/etc/``

- A wsgi file named ``pytheon_wsgi.py`` in ``~/root/lib/``

- A set of binary script in ``~/root/myapp/bin/`` including:

    - A ``pytheon-serve`` script used to run you app through ``supervisord``

    - A ``manage`` script if you use django

    - A ``pytheond`` script (supervisord wrapper)

    - A ``pytheonctl`` script (supervisorctl wrapper)

    - A ``touch-wsgi`` script (only touch pytheon_wsgisupervisorctl wrapper)

- A ``~root/var/log/`` directory to store your log

- A ``~root/var/run/`` directory to store pid files

Using env var for dynamic configuration
=======================================

pytheon use os.environ to store some configuration values. Any variable passed to the command line can be retrieve in your application.

For example, let specify a memcached url:

.. sourcecode:: bash

    $ $PYTHEON_ADMIN -d git://example.com/myapp.git --host=mydomain.com MEMCACHED=localhost:2111

In your application you'll be able to do something like:

.. sourcecode:: python

    memcache = os.environ.get('MEMCACHED_URL', default_value_for_dev)

If you use django then pytheon will understand a few value:

- ``MYSQL_URL`` will populate the default database with mysql

- ``PG_URL`` will populate the default database with postgres

- ``MEMCACHED`` will populate the default cache


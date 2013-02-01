====
Tips
====

You want increase the speed of your deployment ?
================================================

| By default the pytheon bootstrap script install a minimalistic set of eggs.
| These eggs are shared by your installed apps.


At pytheon installation step, you can use the ``--extend`` options to extend
the installation at run time :

.. code-block:: sh

  $ python pytheon_bootstrap.py --extend [django|http://url.to.your/config.cfg]

If the option is a simple term the it will look at the pytheon repository to
find the ``.cfg``.  See the `available files`_

After installation, you can always change this stuff in ``{prefix}/etc/pytheon/pytheon.ini``.

.. code-block:: ini
   :linenos:
   :emphasize-lines: 9-11

    [build_eggs]
    extends = http://download.zope.org/zopetoolkit/index/1.1/ztk-versions.cfg
        https://raw.github.com/pytheon/pytheon.deploy/master/deploy/versions.cfg
    scripts =
        pytheon-admin
        pytheon-eggs
        buildout
        fab
    eggs =
        zc.buildout
        gp.vcsdevelop

Append your eggs after line 11.

You can now build all that stuff :

.. code-block:: sh

  $ bin/build-eggs

By default this will download eggs for the python versions of the interpreter
used to bootstrap pytheon but you can use a different one or more than one :

.. code-block:: sh

  $ bin/build-eggs -i 2.6 -i 3.2

.. _available files: https://github.com/pytheon/pytheon.deploy/tree/master/deploy

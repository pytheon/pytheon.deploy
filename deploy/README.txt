The versions.cfg and dev-versions.cfg are used by pytheon_bootstrap.py to download
``pytheon`` and ``pytheon.deploy`` packages.

``pytheon_boostrap.py`` have ``--branch`` parameter to select the version to use.

Example::

    $ curl -O https://raw.github.com/pytheon/pytheon.deploy/master/deploy/pytheon_bootstrap.py --branch=dev

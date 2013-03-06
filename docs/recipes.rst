========================
pytheon.deploy *recipes*
========================

pytheon.deploy
==============

.. sourcecode:: ini

    recipe = pytheon.deploy
    host=www.example.com

``pytheon.deploy`` recipe achieve :

* develop your eggs (install dependencies…)
* generate `Apache <http://en.wikipedia.org/wiki/Apache_HTTP_Server>`_ configure file ``apache.conf``
* generate `Nginx <http://en.wikipedia.org/wiki/Nginx>`_ configure file ``nginx.conf``
* generate `Supervisor <http://supervisord.org/>`_ configure files ``supervisor.conf`` and ``app-supervisor.conf``
 


``pytheon.deploy`` recipe define some options :


``deploy-dir`` (optional)
    By default : ``parts-directory`` buildout option, by default it is ``parts``.

``host`` (optional)
    You can set your application *hostname* with ``host`` option.

``static`` (optional)

``settings`` (optional)

``bind``

``project_name``

``rundir``
``run_dir``

``extra-paths``

``use``

``password``

``programs``

``autostart``

``autorestart``

``uid``

``gid``

``log_dir``



pytheon.deploy:scripts
======================

.. sourcecode:: ini

    recipe = pytheon.deploy:scripts



pytheon.deploy:wsgi
===================

.. sourcecode:: ini

    recipe = pytheon.deploy:wsgi


pytheon.deploy:apache
=====================

.. sourcecode:: ini

    recipe = pytheon.deploy:apache


pytheon.deploy:nginx
====================

.. sourcecode:: ini

    recipe = pytheon.deploy:nginx

``listen``

``log_dir``

``host``

``locations``

``ssl_certificate``

``ssl_certificate_key``

``document_root``

``www``

``uuid``

``include``

=========================
Application configuration
=========================

Pytheon can deploy any python application with only a few modification

Add a deploy.ini with a deploy section like this:

.. sourcecode:: ini

    [deploy]

Django based application
========================

You need to point your settings.py in the deploy.ini file:

.. sourcecode:: ini

    [deploy]
    settings = myapp/settings.py

pip based application
=====================

If your project contain a ``requirements.txt`` then pytheon will use it to fetch dependencies

Buildout based applications
===========================

You can also use your buildout.cfg instead of a deploy.ini (or use both)

You can add deps as usual:

.. sourcecode:: ini

    [deploy]
    eggs =
        pyramid

.. Note:: You can use this sample application : https://github.com/pytheon/sample_buildout

Handling static files
=====================

You can add some static directories. Those one will be aliased in the web server:

.. sourcecode:: ini

    [deploy]
    static =
        /statics/ = myapp/statics/

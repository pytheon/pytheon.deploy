Supported options
=================

Paste Apps
=============

We'll start by creating a buildout that uses the recipe::

    >>> write('deploy.ini',
    ... """
    ... [server:main]
    ... use = egg:Paste#http
    ... blah = 20
    ...
    ... [app:main]
    ... use = egg:Paste#static
    ... document_root = %(here)s
    ... """)

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = deploy
    ...
    ... [deploy]
    ... version = 1
    ... recipe = pytheon.deploy
    ... use = gunicorn
    ... host = test.pytheon.net
    ... eggs = PasteScript
    ... static_paths =
    ...     /static = %(here)s
    ... """)

Running the buildout gives us::

    >>> print 'start', system(buildout)
    start...
    Installing deploy.
    ...
    Generated script...
    Generated script '/sample-buildout/bin/pytheond'...
    <BLANKLINE>

    >>> cat('parts', 'deploy', 'lib', 'pytheon_wsgi.py')
    #!/...
    import sys
    ...
    application = loadapp("config:" + configfile)
    ...
    <BLANKLINE>

    >>> ls('bin')
    -  b...
    -  pytheon-serve
    ...
    -  touch-wsgi

    >>> cat('parts', 'deploy', 'etc', 'deploy.ini')
    [DEFAULT]
    ...
    [app:main]
    use = egg:Paste#static
    document_root = /sample-buildout
    ...
    <BLANKLINE>

    >>> ls('parts', 'deploy', 'var', 'www')
    d  static

    >>> ls('parts', 'deploy', 'etc')
    -  apache.conf
    -  app-supervisor.conf
    -  deploy.ini
    -  gunicorn_config.py
    -  http_port.txt
    -  nginx.conf
    -  supervisor.conf

    >>> cat('parts', 'deploy', 'etc', 'app-supervisor.conf')
    <BLANKLINE>
    [program:server]
    priority = 0
    process_name = server
    command = .../bin/pytheon-serve
    directory = ...
    autostart = true
    autorestart = true
    redirect_stderr = true
    <BLANKLINE>

    >>> cat('parts', 'deploy', 'etc', 'supervisor.conf')
    [unix_http_server]
    ...
    [supervisord]
    ...
    [supervisorctl]
    ...
    [rpcinterface:supervisor]
    ...
    [include]
    files = 
        .../deploy/etc/app-supervisor.conf
    <BLANKLINE>

Django Apps
=============

Cleaning::

    >>> import os
    >>> os.remove('.installed.cfg')
    >>> os.remove('deploy.ini')

We'll start by creating a buildout that uses the recipe::

    >>> write('deploy.ini', '')

    >>> write('settings.py',
    ... """
    ... DATABASES = {}
    ... """)

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = deploy
    ... extends = deploy.ini
    ...
    ... [deploy]
    ... recipe = pytheon.deploy
    ... eggs = PasteScript
    ... version = 1
    ... use = gunicorn
    ... host = test.pytheon.net
    ... """)

Running the buildout gives us::

    >>> print 'start', system(buildout)
    start...
    Installing deploy.
    ...
    <BLANKLINE>

    >>> cat('parts', 'deploy', 'etc', 'deploy.ini')
    [DEFAULT]
    ...
    [app:main]
    paste.app_factory = pytheon.deploy.django_utils:make_django
    <BLANKLINE>

    >>> ls('bin')
    -  b...
    -  pytheon-serve
    ...
    -  touch-wsgi

We have a ``bin/manage`` script::

    >>> cat('bin', 'manage')
    #!/...
    ...
    import pytheon.deploy.django_utils
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(pytheon.deploy.django_utils.manage('/sample-buildout/parts/deploy/etc/deploy.ini'))

And a ``touch-wsgi`` script::

    >>> cat('bin', 'touch-wsgi')
    #!/...
    import time; t = time.time()
    ...
    if __name__ == '__main__':
        sys.exit(os.utime('/sample-buildout/parts/deploy/lib/pytheon_wsgi.py', (t, t)))

Requirement file
=================

Cleaning::

    >>> import os
    >>> if os.path.isfile('.installed.cfg'): os.remove('.installed.cfg')

We'll start by creating a buildout that uses the recipe::

    >>> write('deploy.ini', '')

    >>> write('settings.py',
    ... """
    ... DATABASES = {}
    ... """)

    >>> write('requirements.txt',
    ... """
    ... Django
    ... -e git+http://github.com/Pylons/webob.git#egg=WebOb
    ... -e git+http://github.com/Pylons/webtest.git#egg=WebTest
    ... """)

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = deploy
    ... extensions = gp.vcsdevelop
    ... requirements = requirements.txt
    ... extends = deploy.ini
    ...
    ... [deploy]
    ... recipe = pytheon.deploy
    ... version = 1
    ... use = gunicorn
    ... host = test.pytheon.net
    ... """)

Running the buildout gives us::

    >>> print 'start', system(buildout + ' -v')
    start...
    Installing deploy.
    ...
    <BLANKLINE>

Assume that WebOb is a dependencie::

    >>> print 'File', cat('bin', 'pytheon-serve')
    File...
    ...'/sample-buildout/WebOb',...
    ...'/sample-buildout/WebTest',...


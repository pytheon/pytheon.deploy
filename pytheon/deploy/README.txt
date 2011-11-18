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
    ...
    ... [deploy]
    ... version = 1
    ... use = gunicorn
    ... host = test.pytheon.net
    ... """)

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = deploy
    ... extends = deploy.ini
    ...
    ... [deploy]
    ... recipe = pytheon.deploy
    ... eggs += PasteScript
    ... static_paths =
    ...     /static = %(here)s
    ... """)

Running the buildout gives us::

    >>> print 'start', system(buildout) 
    start...
    Installing deploy.
    ...
    Generated script...
    Generated script '/sample-buildout/bin/pytheond'.
    <BLANKLINE>

    >>> cat('parts', 'deploy', 'lib', 'pytheon_wsgi.py')
    #!/...
    import sys
    ...
    application = loadapp("config:" + configfile)
    ...
    <BLANKLINE>
    
    >>> ls('bin')
    -  buildout
    -  paster
    -  pytheon-serve
    -  pytheon-update
    -  pytheonctl
    -  pytheond
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

Django Apps
=============

Cleaning::

    >>> import os
    >>> os.remove('.installed.cfg')
    >>> os.remove('deploy.ini')

We'll start by creating a buildout that uses the recipe::

    >>> write('deploy.ini',
    ... """
    ... [deploy]
    ... version = 1
    ... use = gunicorn
    ... host = test.pytheon.net
    ... """)

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
    ... eggs += PasteScript
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
    ...
    <BLANKLINE>

    >>> ls('bin')
    -  buildout
    -  manage
    -  paster
    -  pytheon-serve
    -  pytheon-update
    -  pytheonctl
    -  pytheond
    -  touch-wsgi

We have a ``bin/manage`` script::

    >>> cat('bin', 'manage')
    #!/...
    ...
    import pytheon.deploy.django_utils
    <BLANKLINE>
    if __name__ == '__main__':
        pytheon.deploy.django_utils.manage('/sample-buildout/parts/deploy/etc/deploy.ini')
    
And a ``touch-wsgi`` script::

    >>> cat('bin', 'touch-wsgi')
    #!/...
    import time; t = time.time()
    ...
    if __name__ == '__main__':
        os.utime('/sample-buildout/parts/deploy/lib/pytheon_wsgi.py', (t, t))
    
Requirement file
=================

Cleaning::

    >>> import os
    >>> if os.path.isfile('.installed.cfg'): os.remove('.installed.cfg')

We'll start by creating a buildout that uses the recipe::

    >>> write('deploy.ini',
    ... """
    ... [deploy]
    ... version = 1
    ... use = gunicorn
    ... host = test.pytheon.net
    ... """)

    >>> write('settings.py',
    ... """
    ... DATABASES = {}
    ... """)

    >>> write('requirements.txt',
    ... """
    ... Django
    ... -e hg+https://bitbucket.org/ianb/webob#egg=WebOb
    ... -e hg+https://bitbucket.org/ianb/webtest#egg=WebTest
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
    ... """)

Running the buildout gives us::

    >>> print 'start', system(buildout + ' -v') 
    start...
    Installing deploy.
    ...
    <BLANKLINE>

Assume that WebOb is a dependencie::

    >>> print 'File', cat('parts', 'deploy_django', 'site.py')
    File...
    ...'/sample-buildout/WebOb',...
    ...'/sample-buildout/WebTest',...


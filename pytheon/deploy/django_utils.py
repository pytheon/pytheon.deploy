# -*- coding: utf-8 -*-
import os, sys
from pytheon.utils import log
from pytheon.utils import engine_from_config

def django_settings(config):
    import settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    DATABASES = {}
    CACHES = {}


    engine = engine_from_config({})
    if engine:
        url = engine.url
        database = url.database
        drivername = url.drivername
        if drivername == 'sqlite':
            drivername = 'sqlite3'
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.%s' % drivername,
                'NAME': database,
                'USER': url.username,
                'PASSWORD': url.password,
                'HOST': url.host,
                'PORT': url.port,
            }
        }

    for key, value in (
                ('MEMCACHED', 'django.core.cache.backends.memcached.MemcachedCache'),
                ('DATABASE_CACHE', 'django.core.cache.backends.db.DatabaseCache'),
            ):
        if key in os.environ:
            CACHES = {
                'default': {
                    'BACKEND': value,
                    'LOCATION': os.environ[key],
                }
            }
            break

    log.debug('DATABASES = %r' % DATABASES)
    setattr(settings, 'DATABASES', DATABASES)

    log.debug('CACHES = %r' % CACHES)
    setattr(settings, 'CACHES', CACHES)

    # you should eval at least one var in the real settings module to avoid
    # bugs...
    from django.conf import settings as sets
    _ = sets.DATABASES
    _ = sets.CACHES

    return settings

def patch_file_storage():
    from django.core.files import storage
    import urlparse

    if not os.path.isdir(os.environ['UPLOAD_ROOT']):
        os.makedirs(os.environ['UPLOAD_ROOT'])

    def FileSystemStorage_path(self, name):
        try:
            path = storage.safe_join(os.environ['UPLOAD_ROOT'], name)
        except ValueError:
            raise storage.SuspiciousOperation("Attempted access to '%s' denied." % name)
        return os.path.normpath(path)

    def FileSystemStorage_url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        return urlparse.urljoin('/uploads', storage.filepath_to_uri(name))

    storage.FileSystemStorage.path = FileSystemStorage_path
    storage.FileSystemStorage.url = FileSystemStorage_url

    log.warn('FileSystemStorage patched. /uploads must be bound to %s',
                    os.environ['UPLOAD_ROOT'])

def manage(config):
    from pytheon.utils import Config
    config = Config.from_file(config)
    config = dict(config['app:main'].items())
    settings = django_settings(config)
    from django.core.management import execute_manager
    execute_manager(settings)

def make_django(global_config, **config):
    settings = django_settings(config)
    setattr(settings, 'DEBUG', False)
    setattr(settings, 'TEMPLATE_DEBUG', False)
    import django.core.handlers.wsgi
    application = django.core.handlers.wsgi.WSGIHandler()
    return application


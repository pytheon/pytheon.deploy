# -*- coding: utf-8 -*-
import os
from pytheon.utils import log
from pytheon.utils import engine_from_config


def django_settings(config):
    """return django's settings with modified values extracted from environ to
    set a correct database/cache backends"""
    import settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    DATABASES = getattr(settings, 'DATABASES', {})
    DATABASES_OPTIONS = DATABASES.get('default', {}).get('OPTIONS', {})
    DATABASES = {}
    CACHES = getattr(settings, 'CACHES', {})

    engine = engine_from_config({})
    if engine:
        url = engine.url
        database = url.database
        drivername = url.drivername
        if drivername == 'sqlite':
            drivername = 'sqlite3'
        elif drivername.startswith('postgres'):
            drivername = 'postgresql_psycopg2'
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.%s' % drivername,
                'NAME': database,
                'USER': url.username,
                'PASSWORD': url.password,
                'HOST': url.host,
                'PORT': url.port,
                'OPTIONS': DATABASES_OPTIONS,
            }
        }

    for key, value in (
          ('MEMCACHED', 'django.core.cache.backends.memcached.MemcachedCache'),
          ('DATABASE_CACHE', 'django.core.cache.backends.db.DatabaseCache'),
        ):
        if key in os.environ:
            location = os.environ[key]
            if ',' in location:
                location = location.split(',')
            CACHES.setdefault('default', {})
            for cache in CACHES.values():
                cache.update({
                    'BACKEND': value,
                    'LOCATION': location,
                })
            break

    log.debug('DATABASES = %r' % DATABASES)
    setattr(settings, 'DATABASES', DATABASES)

    log.debug('CACHES = %r' % CACHES)
    setattr(settings, 'CACHES', CACHES)

    # you should eval at least one var in the real settings module to avoid
    # bugs...
    from django.conf import settings as sets
    _ = sets.DATABASES
    log.debug(_)
    _ = sets.CACHES
    log.debug(_)

    return settings


def patch_file_storage():
    # not used
    from django.core.files import storage
    import urlparse

    if not os.path.isdir(os.environ['UPLOAD_ROOT']):
        os.makedirs(os.environ['UPLOAD_ROOT'])

    def FileSystemStorage_path(self, name):
        try:
            path = storage.safe_join(os.environ['UPLOAD_ROOT'], name)
        except ValueError:
            raise storage.SuspiciousOperation(
                        "Attempted access to '%s' denied." % name)
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
    """django's manage wrapper to take care of the configuration"""
    from pytheon.utils import Config
    config = Config.from_file(config)
    config = dict(config['app:main'].items())
    settings = django_settings(config)
    from django.core.management import execute_manager
    execute_manager(settings)


def make_django(global_config, **config):
    """a django wsgi application which take care of the configuration"""
    settings = django_settings(config)
    setattr(settings, 'DEBUG', False)
    setattr(settings, 'TEMPLATE_DEBUG', False)
    import django.core.handlers.wsgi
    application = django.core.handlers.wsgi.WSGIHandler()
    return application

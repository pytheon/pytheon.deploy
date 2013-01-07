# -*- coding: utf-8 -*-
__doc__ = """Monkey patch sys.path to take care of some extra directories"""
import os
import zc.buildout.buildout
import zc.buildout.easy_install
from pytheon.deploy import log


def patch(cls):
    def wrapper(func):
        if not hasattr(cls, '__pytheon__'):
            func(cls)
        return lambda: True
    return wrapper


@patch(zc.buildout.easy_install.Installer)
def buildout_patch(cls):
    """patch used to fetch eggs from an existing repo"""
    ___init__ = cls.__init__
    cls._pytheon_versions = {}

    def __init__(self, *args, **kwargs):
        ___init__(self, *args, **kwargs)
        for env in ('PYTHON_EGGS', 'PYTHEON_EGGS_DIR'):
            if env in os.environ:
                entries = os.environ[env].split(':')
                self._env.scan(entries)
                log.debug('Add %s to Environment', ':'.join(entries))

    cls.__init__ = __init__

# -*- coding: utf-8 -*-
import os
import logging
import pkg_resources
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
        if 'PYTHON_EGGS' in os.environ:
            entries = os.environ['PYTHON_EGGS'].split(':')
            self._env.scan(entries)
            log.debug('Add %s to Environment', ':'.join(entries))
    cls.__init__ = __init__
    #__get_dist = cls._get_dist
    #cls.__picked_versions = {}
    #def _get_dist(self, requirement, ws, always_unzip):
    #    dists = __get_dist(self, requirement, ws, always_unzip)
    #    for dist in dists:
    #        if not (dist.precedence == pkg_resources.DEVELOP_DIST or \
            #                (len(requirement.specs) == 1 and requirement.specs[0][0] == '==')):
    #            self._pytheon_versions[dist.project_name] = dist.version
    #    return dists
    #cls._get_dist = _get_dist



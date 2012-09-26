# -*- coding: utf-8 -*-
from pytheon.utils import Config
from pytheon.utils import log # NOQA
from pytheon import utils
from os.path import join
import os

__all__ = ('CONFIG', 'Config', 'utils', 'log')

ETC_DIR = os.path.join(os.environ.get('PYTHEON_PREFIX', '/'), 'etc', 'pytheon')


EGGS_DIR = os.environ.get('PYTHEON_EGGS_DIR', None)

if not EGGS_DIR:
    for dirname in ('/var/share', '/var/lib'):
        dirname = os.path.join(dirname, 'pytheon', 'eggs')
        if os.path.isdir(dirname):
            EGGS_DIR = dirname

if not EGGS_DIR or not os.path.isdir(EGGS_DIR):
    cfg = Config.from_file(
                os.path.expanduser(join('~', '.buildout', 'default.cfg')))
    EGGS_DIR = cfg.buildout['eggs-directory'] or None

if not EGGS_DIR or not os.path.isdir(EGGS_DIR):
    raise OSError("Can't find pytheon eggs directory")

defaults = dict([('default_%s' % k[8:].lower(), v)
                    for k, v in os.environ.items()
                        if k.startswith('PYTHEON_')])
defaults['here'] = ETC_DIR
defaults['default_eggs_dir'] = EGGS_DIR
os.environ['PYTHON_EGGS'] = EGGS_DIR

if not os.path.isdir(ETC_DIR):
    CONFIG = Config(defaults=defaults)
    CONFIG.pytheon = dict(eggs_dir=EGGS_DIR)
else:
    CONFIG = Config.from_file(join(ETC_DIR, 'pytheon.ini'), **defaults)

utils.CONFIG = CONFIG

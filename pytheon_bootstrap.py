##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Bootstrap a buildout-based project

Simply run this script in a directory containing a buildout.cfg.
The script accepts buildout command-line options, so you can
use the -c option to specify an alternate configuration file.
"""

import os, shutil, sys, tempfile, urllib, urllib2, subprocess
from optparse import OptionParser

if sys.platform == 'win32':
    def quote(c):
        if ' ' in c:
            return '"%s"' % c  # work around spawn lamosity on windows
        else:
            return c
else:
    quote = str

# See zc.buildout.easy_install._has_broken_dash_S for motivation and comments.
stdout, stderr = subprocess.Popen(
    [sys.executable, '-Sc',
     'try:\n'
     '    import ConfigParser\n'
     'except ImportError:\n'
     '    print 1\n'
     'else:\n'
     '    print 0\n'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
has_broken_dash_S = bool(int(stdout.strip()))

# In order to be more robust in the face of system Pythons, we want to
# run without site-packages loaded.  This is somewhat tricky, in
# particular because Python 2.6's distutils imports site, so starting
# with the -S flag is not sufficient.  However, we'll start with that:
if not has_broken_dash_S and 'site' in sys.modules:
    # We will restart with python -S.
    args = sys.argv[:]
    args[0:0] = [sys.executable, '-S']
    args = map(quote, args)
    os.execv(sys.executable, args)
# Now we are running with -S.  We'll get the clean sys.path, import site
# because distutils will do it later, and then reset the path and clean
# out any namespace packages from site-packages that might have been
# loaded by .pth files.
clean_path = sys.path[:]
import site  # imported because of its side effects
sys.path[:] = clean_path
for k, v in sys.modules.items():
    if k in ('setuptools', 'pkg_resources') or (
        hasattr(v, '__path__') and
        len(v.__path__) == 1 and
        not os.path.exists(os.path.join(v.__path__[0], '__init__.py'))):
        # This is a namespace package.  Remove it.
        sys.modules.pop(k)

distribute_source = 'http://python-distribute.org/distribute_setup.py'


# parsing arguments
def normalize_to_url(option, opt_str, value, parser):
    if value:
        if '://' not in value:  # It doesn't smell like a URL.
            value = 'file://%s' % (
                urllib.pathname2url(
                    os.path.abspath(os.path.expanduser(value))),)
        if opt_str == '--download-base' and not value.endswith('/'):
            # Download base needs a trailing slash to make the world happy.
            value += '/'
    else:
        value = None
    name = opt_str[2:].replace('-', '_')
    setattr(parser.values, name, value)

usage = '''\
[DESIRED PYTHON FOR BUILDOUT] pytheon_bootstrap.py [options]

Bootstraps a pytheon-based project.

Simply run this script in a directory containing a buildout.cfg, using the
Python that you want bin/buildout to use.

Note that by using --setup-source and --download-base to point to
local resources, you can keep this script from going over the network.
'''

parser = OptionParser(usage=usage)
parser.add_option("--prefix", default=os.getcwd(),
                  help=("Specify a installation directory"))
parser.add_option("--eggs",
                  help=("Specify a directory for storing eggs.  Defaults to "
                        "a temporary directory that is deleted when the "
                        "bootstrap script completes."))
parser.add_option("-r", "--requirements", dest="requirements",
                  action='append', default=[],
                  help="a set of requirements")

options, args = parser.parse_args()

prefix = os.path.abspath(options.prefix)

share_dir = os.path.join(prefix, 'share', 'pytheon', 'buildout')
if not os.path.isdir(share_dir):
    os.makedirs(share_dir)
os.chdir(prefix)

if os.path.isfile('.installed.cfg'):
    os.remove('.installed.cfg')

if options.eggs:
    eggs_dir = os.path.abspath(os.path.expanduser(options.eggs))
else:
    eggs_dir = os.path.join(prefix, 'share', 'pytheon', 'eggs')

if not os.path.isdir(eggs_dir):
    os.makedirs(eggs_dir)

try:
    import pkg_resources
    import setuptools  # A flag.  Sometimes pkg_resources is installed alone.
    if not hasattr(pkg_resources, '_distribute'):
        raise ImportError
except ImportError:
    ez_code = urllib2.urlopen(
        distribute_source).read().replace('\r\n', '\n')
    ez = {}
    exec ez_code in ez
    setup_args = dict(to_dir=eggs_dir, download_delay=0)
    setup_args['no_fake'] = True
    ez['use_setuptools'](**setup_args)
    if 'pkg_resources' in sys.modules:
        reload(sys.modules['pkg_resources'])
    import pkg_resources
    # This does not (always?) update the default working set.  We will
    # do it.
    for path in sys.path:
        if path not in pkg_resources.working_set.entries:
            pkg_resources.working_set.add_entry(path)

cmd = [quote(sys.executable),
       '-c',
       quote('from setuptools.command.easy_install import main; main()'),
       '-mqNxd',
       quote(eggs_dir)]

if not has_broken_dash_S:
    cmd.insert(1, '-S')

setup_requirement = 'distribute'
ws = pkg_resources.working_set
setup_requirement_path = ws.find(
    pkg_resources.Requirement.parse(setup_requirement)).location
env = dict(
    os.environ,
    PYTHONPATH=setup_requirement_path)

requirement = 'zc.buildout'
cmd.append(requirement)

exitcode = os.spawnle(*([os.P_WAIT, sys.executable] + cmd + [env]))
if exitcode != 0:
    sys.stdout.flush()
    sys.stderr.flush()
    print ("An error occurred when trying to install zc.buildout. "
           "Look above this message for any errors that "
           "were output by easy_install.")
    sys.exit(exitcode)

buildout = os.path.join(share_dir, 'buildout.cfg')
open(buildout, 'w').write('''
[buildout]
parts = bootstrap pytheon
newest = false
prefer-final = true
eggs-directory = %(eggs)s
bin-directory = %(prefix)s/bin
parts-directory = %(share_dir)s/parts
develop-eggs-directory = %(share_dir)s/develop-eggs

[bootstrap]
recipe = z3c.recipe.scripts
eggs = zc.buildout
script-initialization =
    import os
    os.chdir(%(prefix)r)
    if os.path.isfile('.installed.cfg'): os.remove('.installed.cfg')
    os.environ['PYTHEON_EGGS_DIR'] = os.environ['PYTHON_EGGS'] = %(eggs)r
entry-points =
    pytheon-upgrade=zc.buildout.buildout:main
arguments = ['-c', %(buildout)r]
scripts = pytheon-upgrade

[pytheon]
recipe = z3c.recipe.scripts
eggs = %(reqs)s
initialization =
    import os
    os.environ['PYTHEON_EGGS_DIR'] = os.environ['PYTHON_EGGS'] = %(eggs)r
''' % dict(eggs=eggs_dir, prefix=prefix, share_dir=share_dir,
           buildout=buildout, reqs='\n    '.join(options.requirements)))

ws.add_entry(eggs_dir)
ws.require(requirement)
import zc.buildout.buildout
zc.buildout.buildout.main(['-c', buildout])

os.remove('.installed.cfg')


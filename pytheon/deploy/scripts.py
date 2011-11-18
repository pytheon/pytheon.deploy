# -*- coding: utf-8 -*-
import os
import sys
import time
import urllib
import shutil
import tempfile
import subprocess
import logging
import pkg_resources
from glob import glob
from os.path import join
from optparse import OptionParser
from pytheon.deploy import CONFIG
from pytheon.deploy import Config
from pytheon import utils

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

log = utils.log

parser = OptionParser()

def py2dsc():
    dist = pkg_resources.get_distribution('stdeb')
    namespace = {}
    dist.run_script('py2dsc', namespace)
    namespace['runit']()

def admin():
    parser.add_option("-i", "--interpreter", dest="interpreter",
                      action="store", default=sys.executable,
                      help='Default to: ' + sys.executable)
    parser.add_option("-d", "--deploy", dest="source",
                      action="store")
    parser.add_option("-b", "--branch", dest="branch",
                      action="store")
    parser.add_option("-a", "--app-name", dest="app_name",
                      action="store", default=None)
    parser.add_option("--destroy", dest="destroy",
                      action="store")
    parser.add_option("--host", dest="host",
                      action="append", default=[])
    parser.add_option("-r", "--root", dest="root",
                      action="store")
    parser.add_option("-e", "--eggs", dest="eggs",
                      action="store", default=os.path.expanduser('~/eggs'),
                      help='Default to: '+os.path.expanduser('~/eggs'))
    parser.add_option("--develop", dest="develop",
                      action="append", default=[])

    (options, args) = parser.parse_args()

    if 'GIT_DIR' in os.environ:
        del os.environ['GIT_DIR']

    if not options.root:
        parser.error('Invalid root option')

    root = utils.realpath(options.root)

    if not os.path.isdir(options.root):
        parser.error('Invalid root option')

    os.chdir(root)

    def guess_app():
        for ext in ('.hg', '.git'):
            app_dirs = glob(join(root, '*', ext))
            if len(app_dirs) == 1:
                app_dir = os.path.dirname(app_dirs[0])
                return app_dir

    app_dir = guess_app()

    if options.destroy:
        if not app_dir:
            parser.error('No application in %s' % options.root)
        supervisor = join(app_dir, 'bin', 'supervisorctl')
        if os.path.isfile(supervisor):
            utils.call(supervisor, 'shutdown', silent=True)
            time.sleep(0.5)
        shutil.rmtree(options.root)
        sys.exit(0)

    if options.source:
        if app_dir and os.path.isdir(app_dir):
            shutil.rmtree(app_dir)
        if not options.source:
            parser.error('No source option')
        log.info(options.source)
        # .git url or local path are git repositories
        if options.source.endswith('.git') or options.source.startswith('/'):
            if options.app_name:
                utils.call('git', 'clone', '-q', options.source, options.app_name)
            else:
                utils.call('git', 'clone', '-q', options.source)
            app_dir = guess_app()
            log.info(app_dir)
            os.chdir(app_dir)
            if options.branch and options.branch != 'master':
                log.info(os.listdir(os.getcwd()))
                log.info(os.environ)
                utils.call('git', 'checkout', '-b', options.branch, 'origin/%s' % options.branch)
        else:
            if options.app_name:
                utils.call('hg', 'clone', '-q', options.source, options.app_name)
            else:
                utils.call('hg', 'clone', '-q', options.source)
            app_dir = guess_app()
            log.info(app_dir)
            os.chdir(app_dir)
            if options.branch and options.branch != 'master':
                # dont take care of hg branch for now
                pass
    elif app_dir is None:
        parser.error('You must have an existing repository or a deploy url')

    os.chdir(app_dir)
    app_name = os.path.basename(app_dir)

    if os.path.isfile('setup.py'):
        options.develop.insert(0, '.')

    for setup in glob(join(app_dir, '*', 'setup.py')):
        options.develop.append(os.path.dirname(setup))

    for setup in glob(join(app_dir, 'src', '*', 'setup.py')):
        options.develop.append(os.path.dirname(setup))

    var = utils.realpath(root, 'var', 'buildout')

    config = Config.from_template('pytheon.cfg')
    config.buildout['dump-picked-versions-file'] = join(root, 'etc', 'versions.cfg')
    config.buildout['eggs-directory'] = options.eggs or join(var, 'eggs')
    config.buildout['parts-directory'] = join(var, 'parts')
    config.buildout['develop-eggs-directory'] = join(var, 'develop-eggs')
    config.buildout.develop = options.develop
    config.deploy.recipe = 'pytheon.deploy'
    config.deploy['deploy-dir'] = root
    if options.host:
        config.deploy.host = options.host
    config.deploy.environ = ['PYTHEON=1', 'PRODUCTION=1'] + list(args)

    if os.path.isfile('requirements.txt'):
        config.buildout.requirements = 'requirements.txt'

    extends = []
    for filename in ('buildout.cfg', 'deploy-%s.ini' % app_name, 'deploy.ini'):
        filename = utils.realpath(os.getcwd(), filename)
        if os.path.isfile(filename):
            extends.append(filename)
    config.buildout.extends = extends

    buildout = 'pytheon.cfg'
    config.write(buildout)

    env = dict([v.split('=', 1) for v in args if '=' in v])

    utils.buildout(options.interpreter, buildout, eggs=CONFIG.pytheon.eggs_dir, env=env)

    if os.path.isfile('post_install.sh'):
        os.environ.update(env)
        lib_dir = join(root, 'lib')
        if os.path.isfile(os.path.join(lib_dir, 'environ.py')):
            execfile(os.path.join(lib_dir, 'environ.py'))
        utils.call('/bin/bash', 'post_install.sh', env=os.environ)

def build_eggs():

    if os.path.isdir('/var/share/pytheon'):
        os.chdir('/var/share/pytheon')

    for i, interpreter in enumerate(('2.5', '2.6')):
        if os.path.isfile('.installed.cfg'):
            os.unlink('.installed.cfg')
        buildout = 'buildout-%s.cfg' % interpreter
        config = Config.from_template('build_eggs.cfg')
        config.buildout['dump-picked-versions-file'] = 'python%s-versions.cfg' % interpreter
        config.buildout['parts-directory'] = os.path.join(os.getcwd(), 'parts-%s' % interpreter)
        config.buildout.extends = CONFIG.build_eggs.extends
        config.deploy.eggs = CONFIG.build_eggs.eggs
        scripts = ['%s=%s-%s' % (s, s, interpreter) for s in CONFIG.build_eggs.scripts.as_list()]
        config.deploy.scripts = scripts
        config.write(buildout)
        utils.buildout('python%s' % interpreter, buildout=buildout, eggs=os.getcwd())


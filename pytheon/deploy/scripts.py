# -*- coding: utf-8 -*-
import os
import sys
import time
import shutil
import logging
from glob import glob
from os.path import join
from optparse import OptionParser
from pytheon.deploy import CONFIG
from pytheon.deploy import Config
from pytheon import utils

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

log = utils.log

parser = OptionParser()


def cherrypy_serve():
    from pytheon.deploy import wsgiserver3
    config, bind_addr = sys.argv[1:3]
    host, port = bind_addr.split(':')
    bind_addr = (host, int(port))
    from pytheon_wsgi import application
    server = wsgiserver3.CherryPyWSGIServer(bind_addr, application,
                                           server_name='cherrypy')
    server.start()


def admin():

    root = os.path.join(os.getcwd(), 'root')

    parser.add_option("-i", "--interpreter", dest="interpreter",
                      action="store", default=sys.executable,
                      help='Default to: ' + sys.executable)
    parser.add_option("-d", "--deploy", dest="source",
                      action="store", metavar='SOURCE',
                      default=os.environ.get('SOURCE', None),
                      help='Default to $SOURCE if exist.')
    parser.add_option("-b", "--branch", dest="branch",
                      action="store",
                      default=os.environ.get('BRANCH', None),
                      help='Default to $BRANCH if exist')
    parser.add_option("-a", "--app-name", dest="app_name",
                      action="store", default=None)
    parser.add_option("--destroy", dest="destroy",
                      action="store")
    parser.add_option("--host", dest="host",
                      action="append",
                      default=os.environ.get('HOSTS', '').split(';'))
    parser.add_option("-r", "--root", dest="root",
                      action="store", default=root,
                      help='Default to %s' % root)
    parser.add_option("-e", "--eggs", dest="eggs",
                      action="store", default=os.path.expanduser('~/eggs'),
                      help='Default to: ' + os.path.expanduser('~/eggs'))
    parser.add_option("--develop", dest="develop",
                      action="append", default=[], help="Testing only")
    parser.add_option("--develop-dir", dest="develop_dir",
                      default=os.environ.get('DEVELOP_DIR', None),
                      help=("Used for buildout:develop-dir. "
                            "Default to $DEVELOP_DIR if exist"))

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
                utils.call('git', 'clone', '-q', options.source,
                                                 options.app_name)
            else:
                utils.call('git', 'clone', '-q', options.source)
            app_dir = guess_app()
            log.info(app_dir)
            os.chdir(app_dir)
            if not options.branch:
                options.branch = 'master'
            utils.call('git', 'checkout', options.branch)
        else:
            if options.app_name:
                utils.call('hg', 'clone', '-q', options.source,
                                                options.app_name)
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
    config.buildout['dump-picked-versions-file'] = join(root, 'etc',
                                                              'versions.cfg')
    config.buildout['eggs-directory'] = options.eggs or join(var, 'eggs')
    config.buildout['parts-directory'] = join(var, 'parts')
    config.buildout['develop-eggs-directory'] = join(var, 'develop-eggs')
    config.buildout.develop = options.develop
    config.deploy.recipe = 'pytheon.deploy'
    config.deploy['deploy-dir'] = root
    if options.develop_dir:
        config.buildout['develop-dir'] = options.develop_dir
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

    env = os.environ
    env.update(dict([v.split('=', 1) for v in args if '=' in v]))

    utils.buildout(options.interpreter, buildout,
                   eggs=CONFIG.pytheon.eggs_dir, env=env)

    if os.path.isfile('post_install.sh'):
        lib_dir = join(root, 'lib')
        if os.path.isfile(os.path.join(lib_dir, 'environ.py')):
            execfile(os.path.join(lib_dir, 'environ.py'))
        utils.call('/bin/bash', 'post_install.sh', env=os.environ)


def build_eggs(args=None):

    parser.add_option("-i", "--interpreter", dest="interpreters",
                      action="append", default=[])

    if args is not None:
        (options, args) = parser.parse_args(args)
    else:
        (options, args) = parser.parse_args()

    interpreters = options.interpreters or \
                   ['.'.join([str(i) for i in sys.version_info[:2]])]

    bin_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    if 'PYTHEON_EGGS_DIR' in os.environ:
        eggs_dir = os.environ['PYTHEON_EGGS_DIR']
    else:
        eggs_dir = os.path.join(os.getcwd(), 'eggs')

    if 'PYTHEON_PREFIX' in os.environ:
        pwd = os.path.join(os.environ['PYTHEON_PREFIX'], 'lib', 'pytheon')
    else:
        pwd = os.path.dirname(eggs_dir)

    env = os.environ
    env.update(
        PYTHEON_PREFIX=env.get('PYTHEON_PREFIX', pwd),
        PYTHEON_EGGS_DIR=env.get('PYTHEON_EGGS_DIR', eggs_dir))

    os.chdir(pwd)

    for i, interpreter in enumerate(interpreters):
        build_dir = os.path.join(pwd, 'build', interpreter)
        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)
        os.chdir(build_dir)
        if os.path.isfile('.installed.cfg'):
            os.unlink('.installed.cfg')
        buildout = os.path.join(build_dir, 'buildout-%s.cfg' % interpreter)
        config = Config.from_template('build_eggs.cfg')
        config.buildout['bin-directory'] = bin_dir
        config.buildout['eggs-directory'] = eggs_dir
        config.buildout['dump-picked-versions-file'] = os.path.join(
                               eggs_dir, 'python%s-versions.cfg' % interpreter)
        config.buildout.extends = CONFIG.build_eggs.extends
        config.buildout['find-links'] = [
            'https://github.com/pytheon/pytheon/tarball/master#egg=pytheon',
            ('https://github.com/pytheon/pytheon.deploy/tarball/master'
             '#egg=pytheon.deploy'),
          ]
        config.versions = {'none': '0.0'}
        eggs = CONFIG.build_eggs.eggs.as_list()
        for egg in ['pytheon.deploy', 'zc.buildout']:
            if egg not in eggs:
                eggs.insert(0, egg)
        config.deploy.eggs = eggs + ['${buildout:eggs}']
        scripts = CONFIG.build_eggs.scripts.as_list()
        for script in ['buildout', 'pytheon-admin']:
            if script not in scripts:
                scripts.append(script)
        scripts = ['%s=%s-%s' % (s, s, interpreter) for s in scripts]
        config.deploy.scripts = scripts
        config.deploy.initialization = [
            "import os",
            "os.environ['PYTHEON_PREFIX'] = %(PYTHEON_PREFIX)r" % env,
            ("os.environ['PYTHEON_EGGS_DIR'] ="
             "os.environ['PYTHON_EGGS'] = %(PYTHEON_EGGS_DIR)r") % env,
          ]
        config.write(buildout)
        utils.buildout('python%s' % interpreter, buildout=buildout,
                                                 eggs=eggs_dir)


def backup_db():
    parser.usage = '''%prog [options]

    Backup a database. If --url is not specified then the script will try to
    use MYSQL_URL environment variable then .my.cnf to retrieve the correct
    informations (username/password/host/database)'''

    parser.add_option("--url", dest="url", default=None,
                      metavar="MYSQL_URL",
                      help="A valid mysql:// url")
    parser.add_option("--dry-run", dest="dry_run",
                      action='store_true', default=False)
    options, args = parser.parse_args()
    if options.url and options.url.startswith('mysql://'):
        os.environ['MYSQL_URL'] = str(options.url)
    try:
        utils.backup_db(os.path.expanduser('~/'),
                        dry_run=options.dry_run)
    except Exception, e:
        log.exception(e)
        sys.exit(1)


def create_db():
    import string
    import binascii
    valid_chars = string.ascii_letters + string.digits
    chars = binascii.b2a_base64(os.urandom(100))
    chars = [c for c in chars if c in valid_chars]
    password = ''.join(chars)[:12]

    parser.usage = '''%prog [options]

    Create a mysql database'''

    parser.add_option("-u", "--username", dest="username", default=None)
    parser.add_option("-p", "--password", dest="password", default=password,
                      help="A random password is generated if not specified")
    parser.add_option("-n", "--database", dest="database", default=None,
                      help="database name. Default to USERNAME")
    parser.add_option("--drop-db", dest="drop", action='store_true',
                      help="try to drop database first",
                      default=False)
    options, args = parser.parse_args()

    if not options.username:
        parser.error('Username is required')

    if not options.database:
        options.database = options.username

    if options.drop:
        script = 'DROP DATABASE IF EXISTS %(database)s;\n'
    else:
        script = ''
    script += ('CREATE DATABASE `%(database)s` '
               'DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;\n'
               "GRANT ALL PRIVILEGES ON `%(database)s` . * "
               "TO '%(username)s'@'localhost' IDENTIFIED BY '%(password)s';")

    import tempfile
    import subprocess
    data = dict(database=options.database,
                username=options.username,
                password=options.password)
    with tempfile.NamedTemporaryFile(prefix='mysql-',
                                     suffix='.sql') as fd:
            script = script % data
            print script
            fd.write(script)
            fd.flush()
            p = subprocess.call('cat %s|mysql' % fd.name, shell=True)
            if p > 0:
                sys.exit(p)
    print
    print '[client]\nuser=%(username)s\npassword=%(password)s' % data
    print
    print ('MYSQL_URL=mysql://%(username)s:%(password)s@'
           'localhost/%(database)s') % data
